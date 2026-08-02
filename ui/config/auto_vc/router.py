import discord

from database.repositories import get_default_auto_vc_settings
from checks.premium import guild_has_premium

from . import (
    AutoVcMenuView,
    build_auto_vc_embed,
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

    if guild_has_premium(interaction):
        await interaction.message.edit(
            content = None,
            embed = build_auto_vc_manager_embed(
                guild = interaction.guild
            ),
            view = AutoVcManagerView(
                guild_id = interaction.guild.id
            )
        )

        return

    settings = get_default_auto_vc_settings(
        guild_id = interaction.guild.id
    )

    if settings is None:
        await interaction.response.send_message(
            '❌ Something went wrong loading Auto VC settings.',
            ephemeral = True
        )
        return

    await interaction.message.edit(
        content = None,
        embed = build_auto_vc_embed(
            guild = interaction.guild,
            settings = settings
        ),
        view = AutoVcMenuView(auto_vc_id = settings.id)
    )