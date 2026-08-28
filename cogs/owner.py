import discord

from discord.ext import commands

from checks.permissions import bot_owner_ctx
from database.repositories import log_command, get_guilds_with_updates_channel


class OwnerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name = 'servers')
    async def servers_command(
        self,
        ctx: commands.Context,
        invite = 'off'
    ):
        if not bot_owner_ctx(ctx):
            return

        await ctx.message.delete()

        print(f'Server Count: {len(self.bot.guilds)}')

        servers_message = 'Servers:\n'
        
        invites_activated = invite.lower() == 'on'

        for server in self.bot.guilds:
            servers_message += f'{server}'

            if invites_activated:
                try:
                    invite_link = await server.text_channels[0].create_invite()
                
                except Exception:
                    invite_link = 'Failed to get invite link'

                servers_message += f': {invite_link}\n'
            
            else:
                servers_message += '\n'

        if servers_message == 'Servers:\n':
            servers_message += 'None'

        print(servers_message)

        for chunk_start in range(0, len(servers_message), 2000):
            await ctx.author.send(servers_message[chunk_start:chunk_start + 2000])

    @commands.command()
    async def sync(self, ctx: commands.Context):
        if not bot_owner_ctx(ctx):
            return

        synced = await self.bot.tree.sync()

        log_command(
            user_id = ctx.author.id,
            guild_id = ctx.guild.id,
            command_name = 'sync',
        )

        print('Synced Commands to the Tree')

        await ctx.send(f'✅ Synced {len(synced)} command(s) to the tree.')

    @commands.command()
    async def skus(self, ctx: commands.Context):
        if not bot_owner_ctx(ctx):
            return

        skus = await self.bot.fetch_skus()

        if not skus:
            await ctx.send('No SKUs found.')
            return

        skus_message = '\n'.join(
            f'{sku.id} | {sku.name} | {sku.type}'
            for sku in skus
        )

        for sku in skus:
            print(sku.id, sku.name, sku.type)

        await ctx.send(f'```\n{skus_message}\n```')

    @commands.command(name = 'broadcast')
    async def broadcast(self, ctx: commands.Context, *, message: str):
        if not bot_owner_ctx(ctx):
            return

        targets = get_guilds_with_updates_channel()

        if not targets:
            await ctx.send('No servers have an updates channel configured.')
            return

        embed = discord.Embed(
            title = '📢 Synto Update',
            description = message,
            colour = 0x00F3FF
        )

        sent_count = 0
        failed_count = 0

        for guild_id, channel_id in targets:
            channel = self.bot.get_channel(channel_id)

            if not isinstance(channel, discord.abc.Messageable):
                failed_count += 1
                continue

            try:
                await channel.send(embed = embed)
                sent_count += 1

            except discord.HTTPException:
                failed_count += 1

        log_command(
            user_id = ctx.author.id,
            guild_id = ctx.guild.id,
            command_name = 'broadcast'
        )

        await ctx.send(
            f'✅ Broadcast sent to `{sent_count}` server(s). '
            f'Failed for `{failed_count}`.'
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(OwnerCog(bot))