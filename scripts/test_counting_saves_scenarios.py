"""
Exercises the full Counting Saves flow end-to-end against the DEV database,
without needing a live Discord connection - fake Message/Interaction/
Channel stand-ins are used so the real service/UI logic (services/counting.py,
ui/views/counting_save.py, services/counting_saves.py) runs unmodified.

Only ever runs against the DEV database - refuses to run otherwise.

Usage:
    python scripts/test_counting_saves_scenarios.py --dev
"""

import asyncio
import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from settings import settings

from database.repositories import (
    set_counting_channel,
    set_counting_saves_enabled,
    update_current_score,
    get_counting_settings,
    credit_user_saves,
    get_user_save_balance,
    consume_user_save_if_available,
    delete_counting_settings
)
from database.repositories.base import execute

from services.counting import handle_counting_message
from services.counting_saves import handle_counting_save_entitlement
from services.counting_saves_dataclass import CountingSaveRuntime


TEST_GUILD_ID = 333333333333333333
TEST_CHANNEL_ID = 555555555555555555
TEST_USER_ID = 444444444444444444
OTHER_USER_ID = 444444444444444445

results: list[bool] = []


def check(name: str, condition: bool) -> None:
    status = 'PASS' if condition else 'FAIL'
    print(f'[{status}] {name}')
    results.append(condition)


class FakeUser:
    def __init__(self, user_id: int):
        self.id = user_id
        self.bot = False
        self.mention = f'<@{user_id}>'


class FakeSentMessage:
    def __init__(self, channel, content, view):
        self.channel = channel
        self.content = content
        self.view = view
        self.edits: list[dict] = []

    async def edit(self, content = None, view = None):
        self.edits.append({'content': content, 'view': view})
        if content is not None:
            self.content = content
        if view is not None:
            self.view = view


class FakeChannel:
    def __init__(self, channel_id: int):
        self.id = channel_id
        self.sent_messages: list[FakeSentMessage] = []

    async def send(self, content = None, view = None):
        message = FakeSentMessage(self, content, view)
        self.sent_messages.append(message)
        return message


class FakeGuild:
    def __init__(self, guild_id: int):
        self.id = guild_id


class FakeMessage:
    _next_id = 1

    def __init__(self, guild, author, channel, content: str):
        self.guild = guild
        self.author = author
        self.channel = channel
        self.content = content
        self.id = FakeMessage._next_id
        FakeMessage._next_id += 1
        self.added_reactions: list[str] = []

    async def add_reaction(self, emoji: str):
        self.added_reactions.append(emoji)


class FakeInteractionResponse:
    def __init__(self):
        self.sent: list[dict] = []
        self.edited: list[dict] = []

    async def send_message(self, content = None, view = None, ephemeral = False):
        self.sent.append({'content': content, 'view': view, 'ephemeral': ephemeral})

    async def edit_message(self, content = None, view = None):
        self.edited.append({'content': content, 'view': view})


class FakeInteraction:
    def __init__(self, user):
        self.user = user
        self.response = FakeInteractionResponse()


class FakeEntitlement:
    def __init__(self, entitlement_id: int, sku_id: int, user_id: int):
        self.id = entitlement_id
        self.sku_id = sku_id
        self.user_id = user_id
        self.consume_calls = 0

    async def consume(self):
        self.consume_calls += 1


def make_message(guild_id: int, user_id: int, content: str) -> FakeMessage:
    return FakeMessage(
        guild = FakeGuild(guild_id),
        author = FakeUser(user_id),
        channel = FakeChannel(TEST_CHANNEL_ID),
        content = content
    )


async def main() -> None:
    if not settings.dev:
        print('Refusing to run against production - pass --dev.', file = sys.stderr)
        sys.exit(1)

    runtime = CountingSaveRuntime()

    set_counting_channel(TEST_GUILD_ID, TEST_CHANNEL_ID)
    set_counting_saves_enabled(TEST_GUILD_ID, True)
    update_current_score(TEST_GUILD_ID, current_score = 5, last_message_id = 1, last_author_id = 0)
    credit_user_saves(TEST_USER_ID, 2)

    # --- 1. Wrong number offers a pending save instead of failing immediately ---
    msg = make_message(TEST_GUILD_ID, TEST_USER_ID, '7')  # expected was 6
    await handle_counting_message(runtime, msg)

    pending = runtime.get_pending_break(TEST_GUILD_ID)
    channel = msg.channel

    check('wrong number creates a pending break, not an immediate fail', pending is not None)
    check('pending reaction added, not a fail reaction', msg.added_reactions == ['⚠️'])
    check('exactly one offer message sent', len(channel.sent_messages) == 1)

    offer_message = channel.sent_messages[0]
    offer_view = offer_message.view
    check('offer message carries a view with the balance mentioned', '`2` Counting Save' in offer_message.content)
    check("view's .message was set to the sent message", offer_view.message is offer_message)

    # --- 2. Only the breaking user can use the save ---
    wrong_user_interaction = FakeInteraction(FakeUser(OTHER_USER_ID))
    await offer_view.children[0].callback(wrong_user_interaction)

    check(
        'a different user clicking is rejected',
        len(wrong_user_interaction.response.sent) == 1
        and 'Only the person who broke' in wrong_user_interaction.response.sent[0]['content']
    )
    check('pending break still active after wrong-user click', runtime.get_pending_break(TEST_GUILD_ID) is not None)
    check('balance untouched by wrong-user click', get_user_save_balance(TEST_USER_ID) == 2)

    # --- 3. The breaking user successfully uses a save ---
    interaction = FakeInteraction(FakeUser(TEST_USER_ID))
    await offer_view.children[0].callback(interaction)

    check('balance decremented by exactly 1', get_user_save_balance(TEST_USER_ID) == 1)
    check('pending break cleared on successful save', runtime.get_pending_break(TEST_GUILD_ID) is None)
    check(
        'offer message edited to confirm the save',
        len(interaction.response.edited) == 1
        and 'used a Counting Save' in interaction.response.edited[0]['content']
    )
    check('current_score untouched by a successful save', get_counting_settings(TEST_GUILD_ID).current_score == 5)

    # --- 4. Timeout path: no save used in time -> the break actually applies ---
    msg2 = make_message(TEST_GUILD_ID, TEST_USER_ID, '7')  # wrong again, expected still 6
    await handle_counting_message(runtime, msg2)

    pending2 = runtime.get_pending_break(TEST_GUILD_ID)
    offer_view_2 = msg2.channel.sent_messages[0].view

    check('second break also creates a pending state', pending2 is not None)

    await offer_view_2.on_timeout()

    check('pending break cleared after timeout', runtime.get_pending_break(TEST_GUILD_ID) is None)
    check('current_score reset to 0 after timeout', get_counting_settings(TEST_GUILD_ID).current_score == 0)
    check('button disabled after timeout', offer_view_2.children[0].disabled is True)
    check(
        'offer message edited to the final "ruined the count" text',
        'ruined the count at `5`' in offer_view_2.message.edits[-1]['content']
    )

    # --- 5. No balance: rejection, but pending break stays open for the rest of the window ---
    update_current_score(TEST_GUILD_ID, current_score = 5, last_message_id = 1, last_author_id = 0)
    while consume_user_save_if_available(TEST_USER_ID):
        pass
    check('balance drained to 0 for this scenario', get_user_save_balance(TEST_USER_ID) == 0)

    msg3 = make_message(TEST_GUILD_ID, TEST_USER_ID, '7')
    await handle_counting_message(runtime, msg3)
    offer_view_3 = msg3.channel.sent_messages[0].view

    no_balance_interaction = FakeInteraction(FakeUser(TEST_USER_ID))
    await offer_view_3.children[0].callback(no_balance_interaction)

    check(
        'no-balance click is rejected with an upsell',
        len(no_balance_interaction.response.sent) == 1
        and "don't have any Counting Saves" in no_balance_interaction.response.sent[0]['content']
        and no_balance_interaction.response.sent[0]['view'] is not None
    )
    check('pending break still open after a failed no-balance click', runtime.get_pending_break(TEST_GUILD_ID) is not None)

    await offer_view_3.on_timeout()  # clean up this scenario's pending state

    # --- 6. Saves disabled entirely: immediate fail, no offer ---
    set_counting_saves_enabled(TEST_GUILD_ID, False)
    update_current_score(TEST_GUILD_ID, current_score = 5, last_message_id = 1, last_author_id = 0)

    msg4 = make_message(TEST_GUILD_ID, TEST_USER_ID, '7')
    await handle_counting_message(runtime, msg4)

    check('no pending break created when saves are disabled', runtime.get_pending_break(TEST_GUILD_ID) is None)
    check('fail reaction (not pending reaction) used when disabled', msg4.added_reactions == ['❌'])
    check(
        'break applied immediately when disabled',
        len(msg4.channel.sent_messages) == 1
        and 'ruined the count at `5`' in msg4.channel.sent_messages[0].content
    )
    check('current_score reset immediately when disabled', get_counting_settings(TEST_GUILD_ID).current_score == 0)

    set_counting_saves_enabled(TEST_GUILD_ID, True)

    # --- 7. Entitlement purchase credits the balance and is idempotent ---
    balance_before_purchase = get_user_save_balance(TEST_USER_ID)
    entitlement = FakeEntitlement(
        entitlement_id = 987654321,
        sku_id = settings.counting_save_3_sku_id,
        user_id = TEST_USER_ID
    )

    await handle_counting_save_entitlement(entitlement)
    check('3-pack purchase credits 3 saves', get_user_save_balance(TEST_USER_ID) == balance_before_purchase + 3)
    check('entitlement.consume() was called once', entitlement.consume_calls == 1)

    await handle_counting_save_entitlement(entitlement)  # simulate the same event being seen again
    check('re-processing the same entitlement does not double-credit', get_user_save_balance(TEST_USER_ID) == balance_before_purchase + 3)
    check('consume() is not called again for an already-recorded entitlement', entitlement.consume_calls == 1)

    # --- Cleanup ---
    delete_counting_settings(TEST_GUILD_ID)
    execute('DELETE FROM user_counting_saves WHERE user_id IN (%s, %s)', (TEST_USER_ID, OTHER_USER_ID))
    execute('DELETE FROM counting_save_purchases WHERE entitlement_id = %s', (entitlement.id,))

    print()
    if all(results):
        print(f'All {len(results)} scenarios passed.')
    else:
        failed = len(results) - sum(results)
        print(f'{failed}/{len(results)} scenario(s) FAILED - see above.')
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
