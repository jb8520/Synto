import random

import discord

from discord import app_commands
from discord.ext import commands

from database.repositories import log_game


RPS_CHOICES = (
    'rock',
    'paper',
    'scissors'
)

WINNING_MATCHUPS = {
    'rock': 'scissors',
    'paper': 'rock',
    'scissors': 'paper'
}


class GamesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name = 'rps')
    @app_commands.choices(
        choice = [
            app_commands.Choice(
                name = 'Rock',
                value = 'rock'
            ),
            
            app_commands.Choice(
                name = 'Paper',
                value = 'paper'
            ),
            
            app_commands.Choice(
                name = 'Scissors',
                value = 'scissors'
            )
        ]
    )
    async def rps(
        self,
        interaction: discord.Interaction,
        choice: app_commands.Choice[str]
    ):
        user_choice = choice.value
        bot_choice = random.choice(RPS_CHOICES)

        if user_choice == bot_choice:
            result = 'It\'s a tie!'

        elif WINNING_MATCHUPS[user_choice] == bot_choice:
            result = 'You win!'

        else:
            result = 'I win!'

        embed = discord.Embed(
            description = (
                f'You chose **{user_choice.title()}**\n'
                f'I chose **{bot_choice.title()}**\n\n'
                f'**{result}**'
            ),
            colour = 0x00F3FF
        )

        await interaction.response.send_message(
            embed = discord.Embed(
                description = (
                    f'You chose **{user_choice.title()}**\n'
                    f'I chose **{bot_choice.title()}**\n\n'
                    f'**{result}**'
                ),
                colour = 0x00F3FF
            )
        )

        if interaction.guild is not None:
            log_game(
                user_id = interaction.user.id,
                guild_id = interaction.guild.id,
                game_name = 'rps'
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(GamesCog(bot))