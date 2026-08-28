import discord

from ui.config import get_settings_colour

from ui.views.auto_vc import AutoVcButtons


AUTO_VC_CONTROL_PANEL_IMAGE_URL = (
    'https://media.discordapp.net/attachments/876226484363202580/1386148076770824262/new-interface-image-2.png'
)


def build_auto_vc_control_panel_embed(guild_id: int) -> discord.Embed:
    embed = discord.Embed(
        title = 'Auto VC Control Panel',
        description = 'Use this panel to manage your temporary voice channel.',
        colour = get_settings_colour(guild_id)
    )

    embed.set_footer(
        text = 'Use the buttons below to manage your voice channel'
    )

    embed.set_image(
        url = AUTO_VC_CONTROL_PANEL_IMAGE_URL
    )

    return embed


async def send_auto_vc_control_panel(channel: discord.abc.Messageable, guild_id: int) -> None:
    await channel.send(
        embed = build_auto_vc_control_panel_embed(guild_id),
        view = AutoVcButtons()
    )