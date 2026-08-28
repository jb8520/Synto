import discord

from database.models import AutoVCSettings

from database.repositories import (
    get_auto_vc_settings_by_creator_channel,
    get_auto_vc_settings,
    guild_has_premium_cached,
    get_general_settings,
    log_auto_vc
)

from services.auto_vc_dataclass import AutoVcRuntime


AUTO_VC_CONTROL_PANEL_IMAGE_URL = (
    'https://media.discordapp.net/attachments/876226484363202580/1386148076770824262/new-interface-image-2.png'
)

DEFAULT_AUTO_VC_NAME_TEMPLATE = '{name} {number}'
MAX_CHANNEL_NAME_LENGTH = 100

def can_use_auto_vc_setup(
    guild_id: int,
    settings: AutoVCSettings
) -> bool:
    if not settings.is_enabled:
        return False

    if settings.is_default:
        return True

    return guild_has_premium_cached(guild_id)


def describe_auto_vc_status(
    guild_id: int,
    settings: AutoVCSettings
) -> str:
    """Mirrors can_use_auto_vc_setup's exact logic, for display purposes -
    a non-default setup that's still marked "enabled" but has lost premium
    is not actually usable, and shouldn't be shown as plain "Enabled"."""
    if not settings.is_enabled:
        return 'Disabled'

    if settings.is_default:
        return 'Enabled'

    if guild_has_premium_cached(guild_id):
        return 'Enabled'

    return 'Locked (Premium required)'


async def handle_auto_vc_voice_state_update(
    runtime: AutoVcRuntime,
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState
) -> None:
    if before.channel == after.channel:
        return

    await maybe_create_auto_vc(
        runtime = runtime,
        member = member,
        after = after
    )

    await maybe_delete_empty_auto_vc(
        runtime = runtime,
        member = member,
        before = before
    )

    maybe_clear_owner_on_leave(
        runtime = runtime,
        member = member,
        before = before,
        after = after
    )


async def maybe_create_auto_vc(
    runtime: AutoVcRuntime,
    member: discord.Member,
    after: discord.VoiceState
) -> None:
    if after.channel is None:
        return

    if not get_general_settings(member.guild.id).auto_vc_enabled:
        return

    settings = get_auto_vc_settings_by_creator_channel(
        guild_id = member.guild.id,
        vc_creator_id = after.channel.id
    )

    if settings is None:
        return
    
    if not can_use_auto_vc_setup(
        guild_id = member.guild.id,
        settings = settings
    ):
        return

    category = member.guild.get_channel(settings.vc_category_id)

    if not isinstance(category, discord.CategoryChannel):
        return

    member_role = member.guild.get_role(settings.member_role_id)

    if member_role is None:
        return

    number = runtime.next_number(
        guild_id = member.guild.id,
        generator_id = settings.id
    )

    channel_name = format_auto_vc_name(
        settings = settings,
        number = number,
        member = member
    )

    overwrites = build_auto_vc_overwrites(
        guild = member.guild,
        member_role = member_role,
        moderator_role_ids = settings.moderator_role_ids
    )

    channel = await member.guild.create_voice_channel(
        name = channel_name,
        category = category,
        overwrites = overwrites
    )

    runtime.add_channel(
        guild_id = member.guild.id,
        generator_id = settings.id,
        channel_id = channel.id,
        owner_id = member.id,
        number = number
    )

    await member.move_to(channel)

    log_auto_vc(
        user_id = member.id,
        guild_id = member.guild.id,
        auto_vc_type = 'created_channel'
    )


async def maybe_delete_empty_auto_vc(
    runtime: AutoVcRuntime,
    member: discord.Member,
    before: discord.VoiceState
) -> None:
    if before.channel is None:
        return

    temp_vc = runtime.find_by_channel(
        guild_id = member.guild.id,
        channel_id = before.channel.id
    )

    if temp_vc is None:
        return

    if before.channel.members:
        return

    runtime.remove_channel(
        guild_id = member.guild.id,
        generator_id = temp_vc.generator_id,
        channel_id = before.channel.id
    )

    await before.channel.delete()

    log_auto_vc(
        user_id = member.id,
        guild_id = member.guild.id,
        auto_vc_type = 'deleted_channel'
    )


def maybe_clear_owner_on_leave(
    runtime: AutoVcRuntime,
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState
) -> None:
    if before.channel is None:
        return

    if after.channel == before.channel:
        return

    temp_vc = runtime.find_by_channel(
        guild_id = member.guild.id,
        channel_id = before.channel.id
    )

    if temp_vc is None:
        return

    if temp_vc.owner_id != member.id:
        return

    temp_vc.owner_id = None


def build_auto_vc_overwrites(
    guild: discord.Guild,
    member_role: discord.Role,
    moderator_role_ids: list[int]
) -> dict[discord.abc.Snowflake, discord.PermissionOverwrite]:
    overwrites: dict[discord.abc.Snowflake, discord.PermissionOverwrite] = {
        guild.default_role: discord.PermissionOverwrite(
            view_channel = False,
            connect = False
        ),
        member_role: discord.PermissionOverwrite(
            view_channel = True,
            connect = True
        )
    }

    for role_id in moderator_role_ids:
        if role_id == 0:
            continue

        role = guild.get_role(role_id)

        if role is None:
            continue

        overwrites[role] = discord.PermissionOverwrite(
            view_channel = True,
            connect = True
        )

    return overwrites


def format_auto_vc_name(
    settings: AutoVCSettings,
    number: int,
    member: discord.Member
) -> str:
    template = settings.channel_name_template or DEFAULT_AUTO_VC_NAME_TEMPLATE

    name = (
        template
        .replace('{name}', settings.name)
        .replace('{number}', str(number))
        .replace('{member_name}', member.display_name)
        .replace('{username}', member.name)
        .replace('{server}', member.guild.name)
    ).strip()

    if not name:
        name = f'{settings.name} {number}'

    return name[:MAX_CHANNEL_NAME_LENGTH]



def get_owned_auto_vc_channel(
    runtime: AutoVcRuntime,
    interaction: discord.Interaction
) -> discord.VoiceChannel | None:
    if interaction.guild is None:
        return None

    temp_vc = runtime.find_by_owner(
        guild_id = interaction.guild.id,
        owner_id = interaction.user.id
    )

    if temp_vc is None:
        return None

    channel = interaction.guild.get_channel(temp_vc.channel_id)

    if not isinstance(channel, discord.VoiceChannel):
        return None

    return channel


def get_owned_auto_vc_temp_channel(
    runtime: AutoVcRuntime,
    interaction: discord.Interaction
):
    if interaction.guild is None:
        return None

    channel = get_owned_auto_vc_channel(
        runtime = runtime,
        interaction = interaction
    )

    if channel is None:
        return None

    return runtime.find_by_channel(
        guild_id = interaction.guild.id,
        channel_id = channel.id
    )


async def claim_auto_vc_ownership(
    runtime: AutoVcRuntime,
    interaction: discord.Interaction
) -> tuple[bool, str]:
    if interaction.guild is None:
        return False, '❌ This can only be used in a server.'

    if not isinstance(interaction.user, discord.Member):
        return False, '❌ This can only be used in a server.'

    if interaction.user.voice is None or interaction.user.voice.channel is None:
        return False, '❌ You are not in a claimable VC.'

    temp_vc = runtime.find_by_channel(
        guild_id = interaction.guild.id,
        channel_id = interaction.user.voice.channel.id
    )

    if temp_vc is None:
        return False, '❌ You are not in a claimable VC.'

    if temp_vc.owner_id == interaction.user.id:
        return False, '❌ You are already the owner of this voice channel.'

    if temp_vc.owner_id is None:
        temp_vc.owner_id = interaction.user.id

        log_auto_vc(
            user_id = interaction.user.id,
            guild_id = interaction.guild.id,
            auto_vc_type = 'claimed_channel'
        )

        return True, '✅ Success!'

    settings = get_auto_vc_settings(
        auto_vc_id = temp_vc.generator_id
    )

    if settings is None:
        return False, '❌ Something went wrong finding this VC setup.'

    moderator_role_ids = set(settings.moderator_role_ids)

    if any(role.id in moderator_role_ids for role in interaction.user.roles):
        temp_vc.owner_id = interaction.user.id

        log_auto_vc(
            user_id = interaction.user.id,
            guild_id = interaction.guild.id,
            auto_vc_type = 'claimed_channel'
        )

        return True, '✅ Success!'

    return False, '❌ This voice channel already has an owner.'


async def set_owned_auto_vc_connect_permission(
    runtime: AutoVcRuntime,
    interaction: discord.Interaction,
    can_connect: bool
) -> tuple[bool, str]:
    if interaction.guild is None:
        return False, '❌ This can only be used in a server.'

    channel = get_owned_auto_vc_channel(
        runtime = runtime,
        interaction = interaction
    )

    if channel is None:
        return False, '❌ You need to be the owner of a voice channel to use this.'

    temp_vc = runtime.find_by_channel(
        guild_id = interaction.guild.id,
        channel_id = channel.id
    )

    if temp_vc is None:
        return False, '❌ Something went wrong finding this voice channel.'

    settings = get_auto_vc_settings(
        auto_vc_id = temp_vc.generator_id
    )

    if settings is None:
        return False, '❌ Something went wrong finding this VC setup.'

    member_role = interaction.guild.get_role(settings.member_role_id)

    if member_role is None:
        return False, '❌ The configured member role could not be found.'

    permissions = channel.overwrites_for(member_role)
    permissions.connect = can_connect

    await channel.set_permissions(
        member_role,
        overwrite = permissions
    )

    log_auto_vc(
        user_id = interaction.user.id,
        guild_id = interaction.guild.id,
        auto_vc_type = 'unlocked_channel' if can_connect else 'locked_channel'
    )

    if can_connect:
        return True, '✅ Voice channel unlocked.'

    return True, '✅ Voice channel locked.'


async def set_owned_auto_vc_view_permission(
    runtime: AutoVcRuntime,
    interaction: discord.Interaction,
    can_view: bool
) -> tuple[bool, str]:
    if interaction.guild is None:
        return False, '❌ This can only be used in a server.'

    channel = get_owned_auto_vc_channel(
        runtime = runtime,
        interaction = interaction
    )

    if channel is None:
        return False, '❌ You need to be the owner of a voice channel to use this.'

    temp_vc = runtime.find_by_channel(
        guild_id = interaction.guild.id,
        channel_id = channel.id
    )

    if temp_vc is None:
        return False, '❌ Something went wrong finding this voice channel.'

    settings = get_auto_vc_settings(
        auto_vc_id = temp_vc.generator_id
    )

    if settings is None:
        return False, '❌ Something went wrong finding this VC setup.'

    member_role = interaction.guild.get_role(settings.member_role_id)

    if member_role is None:
        return False, '❌ The configured member role could not be found.'

    permissions = channel.overwrites_for(member_role)
    permissions.view_channel = can_view

    await channel.set_permissions(
        member_role,
        overwrite = permissions
    )

    log_auto_vc(
        user_id = interaction.user.id,
        guild_id = interaction.guild.id,
        auto_vc_type = 'unhidden_channel' if can_view else 'hid_channel'
    )

    if can_view:
        return True, '✅ Voice channel shown.'

    return True, '✅ Voice channel hidden.'


async def rename_owned_auto_vc(
    runtime: AutoVcRuntime,
    interaction: discord.Interaction,
    name: str
) -> tuple[bool, str]:
    if interaction.guild is None:
        return False, '❌ This can only be used in a server.'

    channel = get_owned_auto_vc_channel(
        runtime = runtime,
        interaction = interaction
    )

    if channel is None:
        return False, '❌ You need to be the owner of a voice channel to use this.'

    name = name.strip()

    if not 1 <= len(name) <= 100:
        return False, '❌ The name must be between 1 and 100 characters.'

    await channel.edit(name = name)

    log_auto_vc(
        user_id = interaction.user.id,
        guild_id = interaction.guild.id,
        auto_vc_type = 'renamed_channel'
    )

    return True, '✅ Voice channel renamed.'


async def set_owned_auto_vc_user_limit(
    runtime: AutoVcRuntime,
    interaction: discord.Interaction,
    user_limit: int
) -> tuple[bool, str]:
    if interaction.guild is None:
        return False, '❌ This can only be used in a server.'

    if not 0 <= user_limit <= 99:
        return False, '❌ The user limit must be a number between 0 and 99.'

    channel = get_owned_auto_vc_channel(
        runtime = runtime,
        interaction = interaction
    )

    if channel is None:
        return False, '❌ You need to be the owner of a voice channel to use this.'

    await channel.edit(user_limit = user_limit)

    log_auto_vc(
        user_id = interaction.user.id,
        guild_id = interaction.guild.id,
        auto_vc_type = 'set_user_limit'
    )

    if user_limit == 0:
        return True, '✅ User limit removed.'

    return True, f'✅ User limit set to `{user_limit}`.'


async def kick_members_from_owned_auto_vc(
    runtime: AutoVcRuntime,
    interaction: discord.Interaction,
    members: list[discord.Member]
) -> tuple[bool, str]:
    if interaction.guild is None:
        return False, '❌ This can only be used in a server.'

    channel = get_owned_auto_vc_channel(
        runtime = runtime,
        interaction = interaction
    )

    if channel is None:
        return False, '❌ You need to be the owner of a voice channel to use this.'

    if not members:
        return False, '❌ No members were selected.'

    overwrites = channel.overwrites

    kicked_count = 0
    blocked_count = 0

    for member in members:
        if member.id == interaction.user.id:
            continue

        overwrites[member] = discord.PermissionOverwrite(
            connect = False
        )

        blocked_count += 1

        if member.voice is not None and member.voice.channel == channel:
            await member.move_to(None)
            kicked_count += 1

    if blocked_count == 0:
        return False, '❌ No valid members were selected.'

    await channel.edit(overwrites = overwrites)

    log_auto_vc(
        user_id = interaction.user.id,
        guild_id = interaction.guild.id,
        auto_vc_type = 'kicked_user'
    )

    if kicked_count == 0:
        return True, f'✅ Blocked {blocked_count} member{"s" if blocked_count != 1 else ""} from joining.'

    return True, (
        f'✅ Kicked {kicked_count} member{"s" if kicked_count != 1 else ""} '
        f'and blocked {blocked_count} member{"s" if blocked_count != 1 else ""} from joining.'
    )


async def permit_targets_to_owned_auto_vc(
    runtime: AutoVcRuntime,
    interaction: discord.Interaction,
    targets: list[discord.Member | discord.Role]
) -> tuple[bool, str]:
    if interaction.guild is None:
        return False, '❌ This can only be used in a server.'

    channel = get_owned_auto_vc_channel(
        runtime = runtime,
        interaction = interaction
    )

    if channel is None:
        return False, '❌ You need to be the owner of a voice channel to use this.'

    if not targets:
        return False, '❌ No members or roles were selected.'

    overwrites = channel.overwrites

    for target in targets:
        overwrites[target] = discord.PermissionOverwrite(
            view_channel = True,
            connect = True
        )

    await channel.edit(overwrites = overwrites)

    log_auto_vc(
        user_id = interaction.user.id,
        guild_id = interaction.guild.id,
        auto_vc_type = 'permitted_user'
    )

    if len(targets) == 1:
        return True, '✅ Permitted 1 target.'

    return True, f'✅ Permitted {len(targets)} targets.'