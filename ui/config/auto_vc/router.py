import discord

from . import (
    AutoVcManagerView,
    build_auto_vc_manager_embed
)


async def open_auto_vc_config(interaction: discord.Interaction) -> None:
    if interaction.guild is None:
        await interaction.response.send_message(
            '❌ This can only be used in a server.',
            ephemeral = True
        )
        return

    await interaction.message.edit(
        content = None,
        embed = build_auto_vc_manager_embed(
            guild = interaction.guild
        ),
        view = AutoVcManagerView(
            guild_id = interaction.guild.id
        )
    )