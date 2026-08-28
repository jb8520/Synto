from discord import (
    Embed,
    Interaction
)

from database.repositories import get_counting_settings

from .. import get_settings_colour


def build_counting_embed(interaction: Interaction) -> Embed:
    settings = get_counting_settings(interaction.guild.id)

    if settings.channel_id == 0:
        channel = '#channel'
    else:
        discord_channel = interaction.guild.get_channel(settings.channel_id)
        channel = discord_channel.mention if discord_channel is not None else '#channel'

    embed = Embed(
        title = '🔢 Counting Settings',
        colour = get_settings_colour(interaction.guild.id)
    )

    embed.add_field(
        name = 'Counting Channel',
        value = f'> {channel}',
        inline = False
    )

    embed.add_field(
        name = 'Double Count',
        value = f'> {settings.double_count}',
        inline = False
    )

    embed.add_field(
        name = 'Counting Saves',
        value = f'> {settings.counting_saves_enabled}',
        inline = False
    )

    return embed