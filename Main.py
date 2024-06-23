import discord, os, datetime
from discord.ext import commands

import Cogs.Auto_Vc, Cogs.Setup
from Configuration import Auto_Vc, Counting, Welcome_Message

from dotenv import load_dotenv
load_dotenv()

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="?",intents=discord.Intents.all(),case_insensitive=True)
    async def setup_hook(self):
        self.remove_command("help")
        Persistent_Views=[Cogs.Auto_Vc.Auto_Vc_Buttons(),
                          Cogs.Setup.Select_Menu_View(),
                          Auto_Vc.Auto_Vcs_Menu_View(),
                          Auto_Vc.Vc_Creator_View(),
                          Auto_Vc.Vc_Category_View(),
                          Auto_Vc.Member_Role_View(),
                          Auto_Vc.Bypass_Roles_View(),
                          Counting.Counting_Menu_View(),
                          Counting.Counting_Channel_View(),
                          Counting.Counting_Double_Count_View(),
                          Welcome_Message.Welcome_Message_Menu_View(),
                          Welcome_Message.Welcome_Channel_View(),
                          Welcome_Message.Welcome_Message_Activated_View()]
        for View in Persistent_Views:
            self.add_view(View)
        bot.Auto_Vcs={}
        bot.Auto_Vc_Owners={}
        bot.Auto_Vc_Number_Names={}
        bot.Time=datetime.datetime.now()
        bot.Column=None
        Extension="Cogs: "
        Count=0
        for Filename in os.listdir("./Cogs"):
            if Filename.endswith(".py"):
                try:
                    await self.load_extension(f"Cogs.{Filename[:-3]}")
                    Extension+=f"{Filename[:-3]}, "
                    Count+=1
                except Exception as Error:
                    print(f"❌ Failed to load extension {Filename[:-3]}\n{type(Error).__name__}: {Error}")
        print(f"✅ Successfully loaded {Count} {Extension[:-2]}")
    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(name="?help",type=discord.ActivityType.watching))
        print(f"{self.user} is connected to Discord, current latency is {round(self.latency*1000)}ms")

bot=MyBot()

@bot.command()
async def servers_command(ctx):
    if ctx.author.id==int(os.environ["BOT_OWNER_ID"]):
        await ctx.message.delete()
        print(f"Server Count: {len(bot.guilds)}")
        for Server in bot.guilds:
            print(Server)
@bot.command()
async def sync(ctx):
    if ctx.author.id==int(os.environ["BOT_OWNER_ID"]):
        await ctx.message.delete()
        await bot.tree.sync()
        print("Synced Commands to the Tree")

bot.run(os.environ["BOT_TOKEN"])