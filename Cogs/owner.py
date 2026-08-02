from discord.ext import commands

from checks.permissions import bot_owner_ctx
from database.repositories import log_command


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

    @commands.command()
    async def sync(self, ctx: commands.Context):
        if not bot_owner_ctx(ctx):
            return

        await self.bot.tree.sync()

        log_command(
            user_id = ctx.author.id,
            guild_id = ctx.guild.id,
            command_name = 'sync',
        )

        print('Synced Commands to the Tree')

    @commands.command()
    async def skus(self, ctx: commands.Context):
        if not bot_owner_ctx(ctx):
            return
        
        print('test')

        skus = await self.bot.fetch_skus()

        for sku in skus:
            print(sku.id, sku.name, sku.type)


async def setup(bot: commands.Bot):
    await bot.add_cog(OwnerCog(bot))