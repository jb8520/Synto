import discord

from discord import app_commands
from discord.ext import commands

from checks.permissions import admin_only_interaction
from database.repositories import log_command
from services.auto_vc import handle_auto_vc_voice_state_update
from ui.views.auto_vc_panel import send_auto_vc_control_panel



class AutoVcCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name = 'control_panel',
        description = 'Sends the auto VC control panel'
    )
    async def auto_vc_control_panel(
        self,
        interaction: discord.Interaction,
    ) -> None:
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        if interaction.guild is None:
            await interaction.response.send_message(
                '❌ This command can only be used in a server.',
                ephemeral = True
            )
            return

        if interaction.channel is None:
            await interaction.response.send_message(
                '❌ The channel could not be found for this command.',
                ephemeral = True
            )
            return

        await interaction.response.send_message(
            '✅ Control panel sent.',
            ephemeral = True
        )

        await send_auto_vc_control_panel(interaction.channel)

        log_command(
            user_id = interaction.user.id,
            guild_id = interaction.guild.id,
            command_name = 'control_panel'
        )


    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ) -> None:
        await handle_auto_vc_voice_state_update(
            runtime = self.bot.auto_vc_runtime,
            member = member,
            before = before,
            after = after
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoVcCog(bot))