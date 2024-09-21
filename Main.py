import discord
from discord.ext import commands

import os, traceback, datetime

import Checks

import Cogs.Auto_Vc, Cogs.Setup
from Configuration import Auto_Vc, Counting, Welcome_Message

from dotenv import load_dotenv
load_dotenv()


# initialise the bot
class Synto(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='?',
                         intents=discord.Intents.all(),
                         case_insensitive=True)
    
    async def setup_hook(self):
        self.remove_command('help')
        # add the persistent views to the bot
        persistent_ivews=[Cogs.Auto_Vc.Auto_Vc_Buttons(),
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
        for view in persistent_ivews:
            self.add_view(view)
        bot.auto_vcs={}
        bot.auto_vc_owners={}
        bot.auto_vc_number_names={}
        bot.time=datetime.datetime.now()
        # load the cogs
        extension='Cogs: '
        count=0
        for filename in os.listdir('./Cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'Cogs.{filename[:-3]}')
                    extension+=f'{filename[:-3]}, '
                    count+=1
                except Exception as Error:
                    print(f'❌ Failed to load extension {filename[:-3]}\n{type(Error).__name__}: {Error}')
        if extension!='Cogs: ':
            extension=extension[:-2]
        print(f'✅ Successfully loaded {count} {extension}')
    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(name='?help',type=discord.ActivityType.watching))
        print(f'{self.user} is connected to Discord, current latency is {round(self.latency*1000)}ms')

bot=Synto()

# print the servers the bot is in
@bot.command()
async def servers_command(ctx:commands.Context,invite='off'):
    Allowed=Checks.Bot_Owner_Ctx(ctx)
    if not(Allowed):
        return
    await ctx.message.delete()
    print(f'Server Count: {len(bot.guilds)}')
    servers_message='Servers:\n'
    if invite.lower()=='on':
        invites_activated=True
    for server in bot.guilds:
        servers_message+=f'{server}'
        if invites_activated:
            try:
                invite_link=await server.text_channels[0].create_invite()
            except:
                invite_link='Failed to get invite link'
            servers_message+=f': {invite_link}\n'
    if servers_message=='Servers:\n':
        servers_message+='None'
    print(servers_message)

# sync slash commands to the tree 
@bot.command()
async def sync(ctx:commands.Context):
    Allowed=Checks.Bot_Owner_Ctx(ctx)
    if not(Allowed):
        return
    await ctx.message.delete()
    await bot.tree.sync()
    print('Synced Commands to the Tree')


bot.run(os.environ['BOT_TOKEN'])