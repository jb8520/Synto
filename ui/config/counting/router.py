import discord

from . import (
    CountingMenuView,
    build_counting_embed
)


async def open_counting_config(interaction: discord.Interaction) -> None:
    await interaction.message.edit(
        content = None,
        embed = build_counting_embed(interaction),
        view = CountingMenuView()
    )

    return