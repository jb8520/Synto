import discord

from discord import app_commands
from discord.ext import commands

from database.repositories import log_game, get_general_settings

from ui.views.connect4 import Connect4View


class Connect4Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name = 'connect4',
        description = 'Starts a 2 player game of Connect 4.'
    )
    async def connect4(self, interaction: discord.Interaction):
        if interaction.guild is not None and not get_general_settings(interaction.guild.id).games_enabled:
            await interaction.response.send_message(
                '❌ Games are disabled in this server.',
                ephemeral = True
            )
            return

        view = Connect4View()

        await interaction.response.send_message(
            f'{view.display_board()}\n\nConnect 4: Red goes first.',
            view = view,
        )

        if interaction.guild is not None:
            log_game(
                user_id = interaction.user.id,
                guild_id = interaction.guild.id,
                game_name = 'connect4',
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Connect4Cog(bot))