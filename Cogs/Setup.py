import discord
from discord import app_commands
from discord.ext import commands

from Configuration.Counting import Counting_Menu_View
from DataBase.Counting import Configure as Counting_Configure, Query as Counting_Query
from Configuration.Auto_Vc import Auto_Vcs_Menu_View
from DataBase.Auto_Vc import Configure as Auto_Vc_Configure, Query as Auto_Vc_Query
from Configuration.Welcome_Message import Welcome_Message_Menu_View
from DataBase.Welcome_Message import Configure as Welcome_Message_Configure, Query as Welcome_Message_Query

class Select_Menu_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Select_Menu())
class Select_Menu(discord.ui.Select):
    def __init__(self):
        Options=[
            discord.SelectOption(label="Menu",description=""),
            discord.SelectOption(label="Counting",description=""),
            discord.SelectOption(label="Auto Vcs",description=""),
            discord.SelectOption(label="Welcome Message",description="")
        ]
        super().__init__(placeholder="Configuration Options",min_values=1,max_values=1,options=Options,custom_id="select_menu")
    async def callback(self,interaction:discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            Choice=self.values[0]
            if Choice=="Menu":
                View=Select_Menu_View()
                await interaction.response.edit_message(content="Synto Configuration Settings ⚙️",embed=None,view=View)
            elif Choice=="Counting":
                Counting_Configure(interaction.guild.id)
                Channel_id=Counting_Query(interaction.guild.id,'channel_id')
                Double_Count=Counting_Query(interaction.guild.id,'double_count')
                Embed=discord.Embed(title="**Counting Settings ⚙️**",colour=0x00F3FF)
                if Channel_id==0:
                    Embed.add_field(name="Counting Channel",value=f"> #channel",inline=False)
                else:
                    Embed.add_field(name="Counting Channel",value=f"> {interaction.guild.get_channel(Channel_id).mention}",inline=False)
                Embed.add_field(name="Double Count",value=f"> {Double_Count}",inline=False)
                View=Counting_Menu_View()
                await interaction.response.edit_message(content=None,embed=Embed,view=View)
            elif Choice=="Auto Vcs":
                Embed=discord.Embed(title="Auto Voice Channel Settings ⚙️",colour=0x00F3FF)
                Auto_Vc_Configure(interaction.guild.id)
                Vc_Creator_id=Auto_Vc_Query(interaction.guild.id,'vc_creator_id')
                Vc_Category_id=Auto_Vc_Query(interaction.guild.id,'vc_category_id')
                Member_Role_id=Auto_Vc_Query(interaction.guild.id,'member_role')
                Bypass_Roles_ids=Auto_Vc_Query(interaction.guild.id,'bypass_roles')
                if Vc_Creator_id==0:
                    Embed.add_field(name="Auto Vc Creator",value=f"> #channel",inline=False)
                else:
                    Embed.add_field(name="Auto Vc Creator",value=f"> {interaction.guild.get_channel(Vc_Creator_id).mention}",inline=False)
                if Bypass_Roles_ids==0:
                    Embed.add_field(name="Moderator Roles",value=f"> @moderator roles",inline=False)
                else:
                    Roles=""
                    for Role_id in Bypass_Roles_ids:
                        Roles+=f"{interaction.guild.get_role(Role_id).mention}, "
                    Roles=Roles[:-2]
                    Embed.add_field(name="Moderator Roles",value=f"> {Roles}",inline=False)
                if Vc_Category_id==0:
                    Embed.add_field(name="Auto Vc Category",value=f"> #category",inline=False)
                else:
                    Embed.add_field(name="Auto Vc Category",value=f"> {interaction.guild.get_channel(Vc_Category_id).mention}",inline=False)
                if Member_Role_id==0:
                    Embed.add_field(name="Member Role",value=f"> @role",inline=False)
                else:
                    Embed.add_field(name="Member Role",value=f"> {interaction.guild.get_role(Member_Role_id).mention}",inline=False)
                View=Auto_Vcs_Menu_View()
                await interaction.response.edit_message(content=None,embed=Embed,view=View)
            elif Choice=="Welcome Message":
                Embed=discord.Embed(title="Welcome Message Settings ⚙️",colour=0x00F3FF)
                Welcome_Message_Configure(interaction.guild.id)
                Channel_id=Welcome_Message_Query(interaction.guild.id,'channel_id')
                Title=Welcome_Message_Query(interaction.guild.id,'title')
                Description=Welcome_Message_Query(interaction.guild.id,'description')
                Colour=Welcome_Message_Query(interaction.guild.id,'colour')
                Activated=Welcome_Message_Query(interaction.guild.id,'activated')
                if Channel_id==0:
                    Embed.add_field(name="Welcome Channel",value=f"> #channel",inline=False)
                else:
                    Embed.add_field(name="Counting Channel",value=f"> {interaction.guild.get_channel(Channel_id).mention}",inline=False)
                Embed.add_field(name="Title",value=f"> {Title}",inline=False)
                if Description is None:
                    Embed.add_field(name="Description",value="> None",inline=False)
                else:
                    Embed.add_field(name="Description",value=f"> {Description}",inline=False)
                if Colour is None:
                    Embed.add_field(name="Colour",value="> None",inline=False)
                else:
                    Embed.add_field(name="Colour",value=f"> #{Colour}",inline=False)
                if Activated:
                    Activated="On"
                else:
                    Activated="Off"
                Embed.add_field(name="Activated",value=f"> {Activated}",inline=False)
                View=Welcome_Message_Menu_View()
                await interaction.response.edit_message(content=None,embed=Embed,view=View)
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this command",ephemeral=True)

class Setup(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot=bot
    @app_commands.command(name="configuration")
    async def config(self,interaction:discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            View=Select_Menu_View()
            await interaction.response.send_message(content="Synto Configuration Settings ⚙️",ephemeral=False,view=View)
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this command",ephemeral=True)

async def setup(bot:commands.Bot):
    await bot.add_cog(Setup(bot))