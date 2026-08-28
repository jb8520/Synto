import discord

from discord import app_commands
from discord.ext import commands, tasks

from services.premium import (
    premium_upsell,
    premium_status,
    counting_saves_upsell,
    handle_premium_entitlement_update,
    handle_premium_entitlement_delete,
    sync_premium_entitlements
)

from services.counting_saves import (
    handle_counting_save_entitlement,
    sync_counting_save_entitlements
)

from services.supporter_role import handle_support_server_member_join


class PremiumCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self) -> None:
        self.sync_premium_entitlements_loop.start()

    async def cog_unload(self) -> None:
        self.sync_premium_entitlements_loop.cancel()

    # Gateway entitlement events should keep the cache correct in real time,
    # but this periodic reconciliation guards against any events missed
    # during downtime or gateway hiccups.
    @tasks.loop(hours = 6)
    async def sync_premium_entitlements_loop(self) -> None:
        await sync_premium_entitlements(self.bot)
        await sync_counting_save_entitlements(self.bot)

    @sync_premium_entitlements_loop.before_loop
    async def _before_sync_premium_entitlements_loop(self) -> None:
        await self.bot.wait_until_ready()


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
        description = 'Buy Counting Saves to rescue your own broken counts, usable in any server.'
    )
    async def counting_saves(
        self,
        interaction: discord.Interaction
    ) -> None:
        await counting_saves_upsell(interaction = interaction)


    @commands.Cog.listener()
    async def on_entitlement_create(
        self,
        entitlement: discord.Entitlement
    ) -> None:
        await handle_premium_entitlement_update(entitlement = entitlement, bot = self.bot)
        await handle_counting_save_entitlement(entitlement = entitlement, bot = self.bot)


    @commands.Cog.listener()
    async def on_entitlement_update(
        self,
        entitlement: discord.Entitlement
    ) -> None:
        await handle_premium_entitlement_update(entitlement = entitlement, bot = self.bot)
        await handle_counting_save_entitlement(entitlement = entitlement, bot = self.bot)


    @commands.Cog.listener()
    async def on_entitlement_delete(
        self,
        entitlement: discord.Entitlement
    ) -> None:
        await handle_premium_entitlement_delete(entitlement = entitlement)


    @commands.Cog.listener()
    async def on_member_join(
        self,
        member: discord.Member
    ) -> None:
        await handle_support_server_member_join(
            bot = self.bot,
            member = member
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(PremiumCog(bot))