import discord

from discord import app_commands
from discord.ext import commands

from database.repositories import log_command
from services.counting import (
    handle_counting_message,
    handle_deleted_counting_message,
    build_counting_stats_embed
)


class CountingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name = 'counting-stats',
        description = 'Shows this server\'s counting progress, such as the highscore and current count.'
    )
    async def counting_stats(self, interaction: discord.Interaction):
        if interaction.guild is None:
            return

        embed = build_counting_stats_embed(interaction.guild)

        await interaction.response.send_message(
            embed = embed,
            ephemeral = True
        )

        log_command(
            user_id = interaction.user.id,
            guild_id = interaction.guild.id,
            command_name = 'counting_stats'
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await handle_counting_message(
            runtime = self.bot.counting_save_runtime,
            message = message
        )

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        await handle_deleted_counting_message(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(CountingCog(bot))