import discord

from . import (
    GeneralMenuView,
    build_general_embed
)


async def open_general_config(interaction: discord.Interaction) -> None:
    await interaction.message.edit(
        content = None,
        embed = build_general_embed(interaction),
        view = GeneralMenuView()
    )

    return