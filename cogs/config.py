import discord
from discord import app_commands
from discord.ext import commands

from ui.config.main_menu import ConfigMenuView

from checks.permissions import admin_only_interaction
from ui.config.main_menu import build_main_menu_embed

from database.repositories import log_command


class ConfigCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _send_settings_menu(
        self,
        interaction: discord.Interaction,
        command_name: str
    ) -> None:
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return
        
        await interaction.response.send_message(
            content = None,
            embed = build_main_menu_embed(interaction.guild.id),
            view = ConfigMenuView(),
            ephemeral = False
        )
        
        log_command(
            user_id = interaction.user.id,
            guild_id = interaction.guild.id,
            command_name = command_name
        )

    @app_commands.command(
        name = 'settings',
        description = 'Open the Synto settings menu',
    )
    async def settings(self, interaction: discord.Interaction):
        await self._send_settings_menu(
            interaction = interaction,
            command_name = 'settings',
        )

    @app_commands.command(
        name = 'configuration',
        description = 'Open the Synto settings menu',
    )
    async def configuration(self, interaction: discord.Interaction):
        await self._send_settings_menu(
            interaction = interaction,
            command_name = 'configuration',
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ConfigCog(bot))