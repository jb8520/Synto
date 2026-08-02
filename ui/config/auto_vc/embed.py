import discord

from database.models import AutoVCSettings

from .. import SETTINGS_COLOUR


def build_auto_vc_embed(
    guild: discord.Guild,
    settings: AutoVCSettings
) -> discord.Embed:
    creator_channel = '`Not set`'

    if settings.vc_creator_id is not None:
        channel = guild.get_channel(settings.vc_creator_id)

        creator_channel = (
            channel.mention
            if channel is not None
            else '`Unknown channel`'
        )

    category = '`Not set`'

    if settings.vc_category_id is not None:
        discord_category = guild.get_channel(settings.vc_category_id)

        category = (
            discord_category.name
            if discord_category is not None
            else '`Unknown category`'
        )

    member_role = '`Not set`'

    if settings.member_role_id is not None:
        role = guild.get_role(settings.member_role_id)

        member_role = (
            role.mention
            if role is not None
            else '`Unknown role`'
        )

    if not settings.moderator_role_ids:
        moderator_roles = '`None`'

    else:
        role_mentions = []

        for role_id in settings.moderator_role_ids:
            role = guild.get_role(role_id)

            if role is not None:
                role_mentions.append(role.mention)

        moderator_roles = (
            ', '.join(role_mentions)
            if role_mentions
            else '`Unknown roles`'
        )

    configured = '`Yes`' if settings.is_configured else '`No`'
    enabled = '`Yes`' if settings.is_enabled else '`No`'
    default = '`Yes`' if settings.is_default else '`No`'

    embed = discord.Embed(
        title = f'Auto VC Settings: {settings.name}',
        description = 'Configure this Auto VC setup.',
        colour = SETTINGS_COLOUR
    )

    embed.add_field(
        name = 'Auto VC Name',
        value = f'> `{settings.name}`',
        inline = False
    )

    embed.add_field(
        name = 'Channel Name Pattern',
        value = f'> `{settings.channel_name_template}`',
        inline = False
    )

    embed.add_field(
        name = 'VC Creator Channel',
        value = f'> {creator_channel}',
        inline = False
    )

    embed.add_field(
        name = 'VC Category',
        value = f'> {category}',
        inline = False
    )

    embed.add_field(
        name = 'Member Role',
        value = f'> {member_role}',
        inline = False
    )

    embed.add_field(
        name = 'Moderator Roles',
        value = f'> {moderator_roles}',
        inline = False
    )

    embed.add_field(
        name = 'Enabled',
        value = f'> {enabled}',
        inline = True
    )

    embed.add_field(
        name = 'Default',
        value = f'> {default}',
        inline = True
    )

    embed.add_field(
        name = 'Configured',
        value = f'> {configured}',
        inline = True
    )

    return embed