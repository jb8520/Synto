import discord

from database.models.auto_vc import AutoVCSettings
from database.repositories import get_auto_vc_settings_for_guild

from .. import SETTINGS_COLOUR


def build_auto_vc_manager_embed(
    guild: discord.Guild
) -> discord.Embed:
    settings_list = get_auto_vc_settings_for_guild(
        guild_id = guild.id
    )

    embed = discord.Embed(
        title = 'Auto VC Setups',
        description = 'Manage this server\'s Auto VC setups.',
        colour = SETTINGS_COLOUR
    )

    if not settings_list:
        embed.add_field(
            name = 'No Auto VC Setups',
            value = '> No Auto VC setups have been created yet.',
            inline = False
        )
        return embed

    default_settings = next(
        (
            settings
            for settings in settings_list
            if settings.is_default
        ),
        None
    )

    if default_settings is not None:
        embed.add_field(
            name = 'Default Auto VC',
            value = format_auto_vc_manager_row(
                guild = guild,
                settings = default_settings
            ),
            inline = False
        )

    other_settings = [
        settings
        for settings in settings_list
        if not settings.is_default
    ]

    if other_settings:
        value = '\n'.join(
            format_auto_vc_manager_row(
                guild = guild,
                settings = settings
            )
            for settings in other_settings
        )

        embed.add_field(
            name = 'Other Auto VC Setups',
            value = value,
            inline = False
        )

    embed.set_footer(
        text = 'Select an Auto VC setup below to configure it.'
    )

    return embed


def format_auto_vc_manager_row(
    guild: discord.Guild,
    settings: AutoVCSettings
) -> str:
    creator_channel = '`Not set`'

    if settings.vc_creator_id is not None:
        channel = guild.get_channel(settings.vc_creator_id)

        creator_channel = (
            channel.mention
            if channel is not None
            else '`Unknown channel`'
        )

    status = '`Enabled`' if settings.is_enabled else '`Disabled`'
    configured = '`Configured`' if settings.is_configured else '`Not configured`'

    return (
        f'> **{settings.name}**\n'
        f'> Creator: {creator_channel}\n'
        f'> Status: {status} • {configured}'
    )