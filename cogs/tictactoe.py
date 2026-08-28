import discord

from discord import app_commands
from discord.ext import commands

from database.repositories import log_game, get_general_settings

from ui.views.tictactoe import TicTacToeView


class TicTacToeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name = 'tictactoe',
        description = 'Starts a 2 player game of TicTacToe.'
    )
    async def tictactoe(self, interaction: discord.Interaction):
        if interaction.guild is not None and not get_general_settings(interaction.guild.id).games_enabled:
            await interaction.response.send_message(
                '❌ Games are disabled in this server.',
                ephemeral = True
            )
            return

        view = TicTacToeView()

        await interaction.response.send_message(
            'Tic Tac Toe: X goes first.',
            view = view,
        )

        if interaction.guild is not None:
            log_game(
                user_id = interaction.user.id,
                guild_id = interaction.guild.id,
                game_name = 'tictactoe',
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(TicTacToeCog(bot))