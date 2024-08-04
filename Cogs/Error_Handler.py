import discord, os, sys, traceback
from discord import app_commands
from discord.ext import commands

from dotenv import load_dotenv
load_dotenv()



class Error_Handler(commands.Cog):
    def __init__(self,bot:commands.bot):
        self.bot=bot

    async def on_error(self,event, *args, **kwargs):
        Error_Traceback=sys.exc_info()
        print(Error_Traceback)


    @commands.Cog.listener()
    async def on_app_command_error(self,interaction:discord.Interaction,error:app_commands.AppCommandError):
        if hasattr(interaction.command, 'on_error'):
            return

        Cog=interaction.cog
        if Cog:
            if Cog._get_overridden_method(Cog.cog_command_error) is not None:
                return
        
        Ignored_Errors=(commands.CommandNotFound,)
        
        Error=getattr(error,'original',error)


        if isinstance(Error,Ignored_Errors):
            return
        commands.BotMissingPermissions
        Error_Channel=interaction.client.get_guild(os.environ["SUPPORT_SERVER_ID"]).get_channel(os.environ["ERROR_LOG_ID"])
        Embed=discord.Embed(title="App Command Error",colour=0xff0000)
        if isinstance(Error,commands.BadArgument):
            Embed.add_field(name="Error Type:",value="> BotMissingPermissions")
            print(type(error))
            print(error)
            try:
                print(error.args)
                print(error[0])
            except:
                print("error")
            await Error_Channel.send(embed=Embed)
        else:
            traceback.print_exc(error)






class Base_View(discord.ui.View):
    async def on_error(self, interaction: discord.Interaction, error: Exception):
        Error_Channel=interaction.client.get_guild(os.environ["SUPPORT_SERVER_ID"]).get_channel(os.environ["ERROR_LOG_ID"])
        Embed=discord.Embed(title="View Error",colour=0xff0000)
        await interaction.response.send_message(embed=Embed)