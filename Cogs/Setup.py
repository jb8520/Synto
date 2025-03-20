import discord
from discord import app_commands
from discord.ext import commands

import Checks

from Configuration.Counting import Counting_Menu_View
from DataBase.Counting import Configure as Counting_Configure, Query as Counting_Query
from Configuration.Auto_Vc import Auto_Vcs_Menu_View
from DataBase.Auto_Vc import Query as Auto_Vc_Query
from Configuration.Welcome_Message import Welcome_Message_Menu_View
from DataBase.Welcome_Message import Configure as Welcome_Message_Configure, Query as Welcome_Message_Query

class Select_Menu_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Select_Menu())
class Select_Menu(discord.ui.Select):
    def __init__(self):
        Options=[
            discord.SelectOption(label='Menu',description=''),
            discord.SelectOption(label='Counting',description=''),
            discord.SelectOption(label='Auto Vcs',description=''),
            discord.SelectOption(label='Welcome Message',description='')
        ]
        super().__init__(placeholder='Configuration Options',min_values=1,max_values=1,options=Options,custom_id='select_menu')
    async def callback(self,interaction:discord.Interaction):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        Choice=self.values[0]
        if Choice=='Menu':
            View=Select_Menu_View()
            await interaction.response.edit_message(content='Synto Configuration Settings ⚙️',embed=None,view=View)
        elif Choice=='Counting':
            Embed=discord.Embed(title='**Counting Settings ⚙️**',colour=0x00F3FF)
            channel_id,highscore,current_score,message_id,author_id,double_count=Counting_Query(interaction.guild.id)
            if channel_id==0:
                Embed.add_field(name='Counting Channel',value=f'> #channel',inline=False)
            else:
                Embed.add_field(name='Counting Channel',value=f'> {interaction.guild.get_channel(channel_id).mention}',inline=False)
            Embed.add_field(name='Double Count',value=f'> {double_count}',inline=False)
            View=Counting_Menu_View()
            await interaction.response.edit_message(content=None,embed=Embed,view=View)
        elif Choice=='Auto Vcs':
            Embed=discord.Embed(title='Auto Voice Channel Settings ⚙️',colour=0x00F3FF)
            vc_creator_id,vc_category_id,member_role_id,moderator_roles_ids_list=Auto_Vc_Query(interaction.guild.id)
            if vc_creator_id==0:
                Embed.add_field(name='Auto Vc Creator',value=f'> #channel',inline=False)
            else:
                Embed.add_field(name='Auto Vc Creator',value=f'> {interaction.guild.get_channel(vc_creator_id).mention}',inline=False)
            if moderator_roles_ids_list==0:
                Embed.add_field(name='Moderator Roles',value=f'> @moderator roles',inline=False)
            else:
                Roles=''
                for Role_id in moderator_roles_ids_list:
                    Roles+=f'{interaction.guild.get_role(Role_id).mention}, '
                Roles=Roles[:-2]
                Embed.add_field(name='Moderator Roles',value=f'> {Roles}',inline=False)
            if vc_category_id==0:
                Embed.add_field(name='Auto Vc Category',value=f'> #category',inline=False)
            else:
                Embed.add_field(name='Auto Vc Category',value=f'> {interaction.guild.get_channel(vc_category_id).mention}',inline=False)
            if member_role_id==0:
                Embed.add_field(name='Member Role',value=f'> @role',inline=False)
            else:
                Embed.add_field(name='Member Role',value=f'> {interaction.guild.get_role(member_role_id).mention}',inline=False)
            View=Auto_Vcs_Menu_View()
            await interaction.response.edit_message(content=None,embed=Embed,view=View)
        elif Choice=='Welcome Message':
            hdgf #- welcome message db stuff need be updated
            Embed=discord.Embed(title='Welcome Message Settings ⚙️',colour=0x00F3FF)
            channel_id,title,description,colour,activated=Welcome_Message_Query(interaction.guild.id)
            Welcome_Message_Configure(interaction.guild.id)
            # Channel_id=Welcome_Message_Query(interaction.guild.id,'channel_id')
            # Title=Welcome_Message_Query(interaction.guild.id,'title')
            # Description=Welcome_Message_Query(interaction.guild.id,'description')
            # Colour=Welcome_Message_Query(interaction.guild.id,'colour')
            # Activated=Welcome_Message_Query(interaction.guild.id,'activated')
            if channel_id==0:
                Embed.add_field(name='Welcome Channel',value=f'> #channel',inline=False)
            else:
                Embed.add_field(name='Counting Channel',value=f'> {interaction.guild.get_channel(channel_id).mention}',inline=False)
            Embed.add_field(name='Title',value=f'> {title}',inline=False)
            if description is None:
                Embed.add_field(name='Description',value='> None',inline=False)
            else:
                Embed.add_field(name='Description',value=f'> {description}',inline=False)
            if colour is None:
                Embed.add_field(name='Colour',value='> None',inline=False)
            else:
                Embed.add_field(name='Colour',value=f'> #{colour}',inline=False)
            if activated:
                activated='On'
            else:
                activated='Off'
            Embed.add_field(name='Activated',value=f'> {activated}',inline=False)
            View=Welcome_Message_Menu_View()
            await interaction.response.edit_message(content=None,embed=Embed,view=View)

class Setup(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot=bot
    @app_commands.command(name='configuration')
    async def config(self,interaction:discord.Interaction):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        View=Select_Menu_View()
        await interaction.response.send_message(content='Synto Configuration Settings ⚙️',ephemeral=False,view=View)

async def setup(bot:commands.Bot):
    await bot.add_cog(Setup(bot))