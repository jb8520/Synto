from discord import Embed, Interaction

from database.repositories import (
    get_general_settings,
    get_welcome_message_settings,
    guild_has_premium_cached
)

from .. import get_settings_colour


def build_general_embed(interaction: Interaction) -> Embed:
    settings = get_general_settings(interaction.guild.id)
    welcome_settings = get_welcome_message_settings(interaction.guild.id)

    if settings.admin_role_ids:
        admin_roles = ', '.join(f'<@&{role_id}>' for role_id in settings.admin_role_ids)

    else:
        admin_roles = '`None set`'

    if settings.normalised_colour is None:
        embed_colour = '`Not set`'

    elif guild_has_premium_cached(interaction.guild.id):
        embed_colour = f'`#{settings.normalised_colour}`'

    else:
        # The colour is still saved, but ignored while this server lacks
        # Premium - get_settings_colour() already falls back to the
        # default everywhere it's used, this just makes that visible here
        # instead of misleadingly showing the saved colour as if it's live.
        embed_colour = f'`#{settings.normalised_colour}` - 🔒 Locked (Premium required, using default colour)'

    if settings.updates_channel_id == 0:
        updates_channel = '`Not set`'

    else:
        discord_channel = interaction.guild.get_channel(settings.updates_channel_id)
        updates_channel = (
            discord_channel.mention
            if discord_channel is not None
            else '`Unknown channel`'
        )

    embed = Embed(
        title = '🛠️ General Settings',
        description = 'Server-wide settings that apply across every Synto feature.',
        colour = get_settings_colour(interaction.guild.id)
    )

    embed.add_field(
        name = 'Admin Roles',
        value = f'> {admin_roles}',
        inline = False
    )

    embed.add_field(
        name = 'Embed Colour (Premium)',
        value = f'> {embed_colour}',
        inline = False
    )

    embed.add_field(
        name = 'Updates Channel',
        value = f'> {updates_channel}',
        inline = False
    )

    embed.add_field(
        name = 'Auto VC',
        value = f'> {settings.auto_vc_enabled}',
        inline = False
    )

    embed.add_field(
        name = 'Counting',
        value = f'> {settings.counting_enabled}',
        inline = False
    )

    embed.add_field(
        name = 'Games',
        value = f'> {settings.games_enabled}',
        inline = False
    )

    embed.add_field(
        name = 'Welcome Message',
        value = f'> {welcome_settings.status}',
        inline = False
    )

    return embed
