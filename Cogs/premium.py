import discord

from discord import app_commands
from discord.ext import commands

from services.premium import (
    premium_upsell,
    premium_status,
    counting_saves_upsell,
    handle_premium_entitlement_update,
    sync_premium_entitlements
)


class PremiumCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def cog_load(self) -> None:
        await sync_premium_entitlements(self.bot)


    @app_commands.command(
        name = 'premium',
        description = 'View Synto Premium for this server.'
    )
    async def premium(
        self,
        interaction: discord.Interaction
    ) -> None:
        await premium_upsell(interaction = interaction)


    @app_commands.command(
        name = 'premium-status',
        description = 'Check whether this server has Synto Premium.'
    )
    async def premium_status(
        self,
        interaction: discord.Interaction
    ) -> None:
        await premium_status(interaction = interaction)


    @app_commands.command(
        name = 'counting-saves',
        description = 'Buy Counting Saves for this server.'
    )
    async def counting_saves(
        self,
        interaction: discord.Interaction
    ) -> None:
        counting_saves_upsell(interaction = interaction)


    @commands.Cog.listener()
    async def on_entitlement_create(
        self,
        entitlement: discord.Entitlement
    ) -> None:
        await handle_premium_entitlement_update(entitlement = entitlement)


    @commands.Cog.listener()
    async def on_entitlement_update(
        self,
        entitlement: discord.Entitlement
    ) -> None:
        await handle_premium_entitlement_update(entitlement = entitlement)


    @commands.Cog.listener()
    async def on_entitlement_delete(
        self,
        entitlement: discord.Entitlement
    ) -> None:
        await handle_premium_entitlement_update(entitlement = entitlement)


async def setup(bot: commands.Bot):
    await bot.add_cog(PremiumCog(bot))