"""
Exercises General Settings behaviour against the DEV database: admin roles
override, per-feature toggle enforcement, and premium-gated embed colour.

Only ever runs against the DEV database - refuses to run otherwise.

Usage:
    python scripts/test_general_settings_scenarios.py --dev
"""

import asyncio
import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from settings import settings

from database.repositories import (
    get_general_settings,
    set_auto_vc_module_enabled,
    set_counting_module_enabled,
    set_games_module_enabled,
    set_general_admin_roles,
    set_general_embed_colour,
    set_guild_premium_status,
    clear_guild_premium_status,
    set_counting_channel,
    update_current_score
)
from database.repositories.base import execute

import services.auto_vc as auto_vc_service
from services.counting import handle_counting_message
from services.counting_saves_dataclass import CountingSaveRuntime

import checks.permissions as permissions_module
from ui.config import get_settings_colour


TEST_GUILD_ID = 777777777777777777
TEST_CHANNEL_ID = 888888888888888888
ADMIN_ROLE_ID = 999999999999999991
NON_ADMIN_ROLE_ID = 999999999999999992

results: list[bool] = []


def check(name: str, condition: bool) -> None:
    status = 'PASS' if condition else 'FAIL'
    print(f'[{status}] {name}')
    results.append(condition)


class FakeRole:
    def __init__(self, role_id: int):
        self.id = role_id


class FakeGuildPermissions:
    def __init__(self, administrator: bool = False):
        self.administrator = administrator


class FakeMember:
    def __init__(self, user_id: int, role_ids: list[int], is_admin: bool = False):
        self.id = user_id
        self.roles = [FakeRole(role_id) for role_id in role_ids]
        self.guild_permissions = FakeGuildPermissions(administrator = is_admin)


class FakeGuild:
    def __init__(self, guild_id: int):
        self.id = guild_id


class FakeInteractionResponse:
    def __init__(self):
        self.sent: list[dict] = []

    async def send_message(self, content = None, ephemeral = False):
        self.sent.append({'content': content, 'ephemeral': ephemeral})


class FakeInteraction:
    def __init__(self, user, guild):
        self.user = user
        self.guild = guild
        self.response = FakeInteractionResponse()


async def main() -> None:
    if not settings.dev:
        print('Refusing to run against production - pass --dev.', file = sys.stderr)
        sys.exit(1)

    # --- 1. Admin roles override ---
    set_general_admin_roles(TEST_GUILD_ID, [ADMIN_ROLE_ID])

    member_with_admin_role = FakeMember(101, [ADMIN_ROLE_ID], is_admin = False)
    interaction_with_role = FakeInteraction(member_with_admin_role, FakeGuild(TEST_GUILD_ID))
    allowed, _ = await permissions_module.admin_only_interaction(interaction_with_role)
    check('member with a configured admin role (no Administrator perm) passes admin_only_interaction', allowed is True)

    member_without_role = FakeMember(102, [NON_ADMIN_ROLE_ID], is_admin = False)
    interaction_without_role = FakeInteraction(member_without_role, FakeGuild(TEST_GUILD_ID))
    allowed, _ = await permissions_module.admin_only_interaction(interaction_without_role)
    check('member without the configured role and without Administrator is rejected', allowed is False)
    check('rejection sends an ephemeral error message', interaction_without_role.response.sent[0]['ephemeral'] is True)

    member_real_admin = FakeMember(103, [], is_admin = True)
    interaction_real_admin = FakeInteraction(member_real_admin, FakeGuild(TEST_GUILD_ID))
    allowed, _ = await permissions_module.admin_only_interaction(interaction_real_admin)
    check('a real Discord Administrator still passes regardless of role config', allowed is True)

    # --- 2. Feature toggle round trip ---
    set_auto_vc_module_enabled(TEST_GUILD_ID, False)
    set_counting_module_enabled(TEST_GUILD_ID, False)
    set_games_module_enabled(TEST_GUILD_ID, False)

    disabled_settings = get_general_settings(TEST_GUILD_ID)
    check(
        'all three module toggles persist as disabled',
        not disabled_settings.auto_vc_enabled
        and not disabled_settings.counting_enabled
        and not disabled_settings.games_enabled
    )

    set_auto_vc_module_enabled(TEST_GUILD_ID, True)
    set_counting_module_enabled(TEST_GUILD_ID, True)
    set_games_module_enabled(TEST_GUILD_ID, True)

    enabled_settings = get_general_settings(TEST_GUILD_ID)
    check(
        'all three module toggles persist as re-enabled',
        enabled_settings.auto_vc_enabled
        and enabled_settings.counting_enabled
        and enabled_settings.games_enabled
    )

    # --- 3. Counting module toggle actually blocks message processing ---
    set_counting_channel(TEST_GUILD_ID, TEST_CHANNEL_ID)
    update_current_score(TEST_GUILD_ID, current_score = 5, last_message_id = 1, last_author_id = 0)
    set_counting_module_enabled(TEST_GUILD_ID, False)

    class FakeUser:
        def __init__(self, user_id):
            self.id = user_id
            self.bot = False
            self.mention = f'<@{user_id}>'

    class FakeChannel:
        def __init__(self, channel_id):
            self.id = channel_id
            self.sent_messages = []

        async def send(self, content = None, view = None):
            self.sent_messages.append(content)

    class FakeMessage:
        def __init__(self, guild_id, user_id, content, channel):
            self.guild = FakeGuild(guild_id)
            self.author = FakeUser(user_id)
            self.channel = channel
            self.content = content
            self.id = 12345
            self.added_reactions = []

        async def add_reaction(self, emoji):
            self.added_reactions.append(emoji)

    channel = FakeChannel(TEST_CHANNEL_ID)
    msg = FakeMessage(TEST_GUILD_ID, 201, '6', channel)  # correct next number
    runtime = CountingSaveRuntime()

    await handle_counting_message(runtime, msg)

    check(
        'counting is fully inert when the module toggle is disabled',
        len(channel.sent_messages) == 0 and len(msg.added_reactions) == 0
    )

    set_counting_module_enabled(TEST_GUILD_ID, True)

    msg2 = FakeMessage(TEST_GUILD_ID, 201, '6', channel)
    await handle_counting_message(runtime, msg2)

    check(
        'counting resumes processing once the module toggle is re-enabled',
        msg2.added_reactions == ['✅']
    )

    # --- 4. Auto VC module toggle short-circuits before any settings lookup ---
    lookup_was_called = False
    original_lookup = auto_vc_service.get_auto_vc_settings_by_creator_channel

    def _tripwire(*args, **kwargs):
        nonlocal lookup_was_called
        lookup_was_called = True
        return original_lookup(*args, **kwargs)

    auto_vc_service.get_auto_vc_settings_by_creator_channel = _tripwire

    set_auto_vc_module_enabled(TEST_GUILD_ID, False)

    class FakeVoiceChannel:
        def __init__(self, channel_id):
            self.id = channel_id

    class FakeVoiceState:
        def __init__(self, channel):
            self.channel = channel

    class FakeAutoVcMember:
        def __init__(self, guild_id):
            self.guild = FakeGuild(guild_id)

    await auto_vc_service.maybe_create_auto_vc(
        runtime = None,
        member = FakeAutoVcMember(TEST_GUILD_ID),
        after = FakeVoiceState(FakeVoiceChannel(999))
    )

    check('auto_vc module toggle short-circuits before any setup lookup', lookup_was_called is False)

    auto_vc_service.get_auto_vc_settings_by_creator_channel = original_lookup
    set_auto_vc_module_enabled(TEST_GUILD_ID, True)

    # --- 5. Embed colour respects premium gating ---
    clear_guild_premium_status(TEST_GUILD_ID)
    set_general_embed_colour(TEST_GUILD_ID, '00FF00')

    check(
        'non-premium guild ignores its stored colour and falls back to default',
        get_settings_colour(TEST_GUILD_ID) != 0x00FF00
    )

    set_guild_premium_status(
        guild_id = TEST_GUILD_ID,
        is_premium = True,
        entitlement_id = 1,
        sku_id = settings.synto_premium_sku_id,
        premium_ends_at = None
    )

    check(
        'premium guild with a stored colour gets that exact colour',
        get_settings_colour(TEST_GUILD_ID) == 0x00FF00
    )

    set_general_embed_colour(TEST_GUILD_ID, None)

    check(
        'premium guild with no stored colour falls back to default',
        get_settings_colour(TEST_GUILD_ID) != 0x00FF00
    )

    # --- Cleanup ---
    clear_guild_premium_status(TEST_GUILD_ID)
    execute('DELETE FROM general_settings WHERE guild_id = %s', (TEST_GUILD_ID,))
    execute('DELETE FROM general_admin_roles WHERE guild_id = %s', (TEST_GUILD_ID,))
    execute('DELETE FROM counting_settings WHERE guild_id = %s', (TEST_GUILD_ID,))

    print()
    if all(results):
        print(f'All {len(results)} scenarios passed.')
    else:
        failed = len(results) - sum(results)
        print(f'{failed}/{len(results)} scenario(s) FAILED - see above.')
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
