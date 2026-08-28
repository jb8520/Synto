import datetime
from pathlib import Path

import discord

from discord import app_commands
from discord.ext import commands

from database.repositories import log_command

from ui.views.bot_info import BuyMeACoffeeView


IGNORED_LINE_COUNT_DIRS = {
    '.git',
    '.venv',
    'venv',
    '__pycache__',
    '.mypy_cache',
    '.pytest_cache'
}


def count_python_lines(root: Path = Path('.')) -> int:
    total_lines = 0

    for file_path in root.rglob('*.py'):
        if any(part in IGNORED_LINE_COUNT_DIRS for part in file_path.parts):
            continue

        try:
            with file_path.open('r', encoding = 'utf-8') as file:
                total_lines += sum(1 for _ in file)

        except OSError:
            continue

    return total_lines


class BotInfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name = 'ping', description = 'Shows the bot latency.')
    async def ping(self, interaction: discord.Interaction):
        latency_ms = round(self.bot.latency * 1000)

        await interaction.response.send_message(
            f'Pong! Latency: `{latency_ms}ms`',
            ephemeral = True
        )

        if interaction.guild is not None:
            log_command(
                user_id = interaction.user.id,
                guild_id = interaction.guild.id,
                command_name = 'ping'
            )

    @app_commands.command(name = 'bot-info', description = 'Shows information about the bot.')
    async def app_info(self, interaction: discord.Interaction):
        started_at = getattr(self.bot, 'time', None)

        if isinstance(started_at, datetime.datetime):
            uptime = f'<t:{int(started_at.timestamp())}:R>'
        
        else:
            uptime = 'Unknown'

        latency_ms = round(self.bot.latency * 1000)
        total_lines = count_python_lines()

        embed = discord.Embed(
            title = 'Bot Status',
            colour = 0x00F3FF
        )

        embed.add_field(
            name = 'Uptime',
            value = f'> {uptime}',
            inline = False
        )

        embed.add_field(
            name = 'Ping',
            value = f'> `{latency_ms}ms`',
            inline = False
        )

        embed.add_field(
            name = 'Lines of Code',
            value = f'> `{total_lines:,}`',
            inline = False
        )

        await interaction.response.send_message(
            embed = embed,
            ephemeral = True
        )

        if interaction.guild is not None:
            log_command(
                user_id = interaction.user.id,
                guild_id = interaction.guild.id,
                command_name = 'bot_info'
            )

    @app_commands.command(
        name = 'buy-me-a-coffee',
        description = 'Support Synto\'s development with a donation.'
    )
    async def buy_me_a_coffee(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title = '☕ Support Synto',
            description = 'If you enjoy using Synto, consider supporting its development with a coffee!',
            colour = 0x00F3FF
        )

        await interaction.response.send_message(
            embed = embed,
            view = BuyMeACoffeeView()
        )

        if interaction.guild is not None:
            log_command(
                user_id = interaction.user.id,
                guild_id = interaction.guild.id,
                command_name = 'buy_me_a_coffee'
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(BotInfoCog(bot))