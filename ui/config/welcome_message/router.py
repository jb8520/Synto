import discord

from . import (
    WelcomeMessageMenuView,
    build_welcome_message_embed
)


async def open_welcome_message_config(interaction: discord.Interaction) -> None:
    await interaction.message.edit(
        content = None,
        embed = build_welcome_message_embed(interaction),
        view = WelcomeMessageMenuView()
    )

    return