from discord import Member
from discord.ext import commands

from services.welcome_message import send_welcome_message


class WelcomeMessageCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        await send_welcome_message(self.bot, member)
    

async def setup(bot: commands.Bot):
    await bot.add_cog(WelcomeMessageCog(bot))