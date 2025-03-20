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
                channel='#channel'
            else:
                try:
                    channel=interaction.guild.get_channel(channel_id).mention
                except:
                    channel='#channel'
            Embed.add_field(name='Counting Channel',value=f'> {channel}',inline=False)
            Embed.add_field(name='Double Count',value=f'> {double_count}',inline=False)
            view=Counting_Menu_View()
            await interaction.response.edit_message(content=None,embed=Embed,view=view)
        elif Choice=='Auto Vcs':
            Embed=discord.Embed(title='Auto Voice Channel Settings ⚙️',colour=0x00F3FF)
            vc_creator_id,vc_category_id,member_role_id,moderator_roles_ids_list=Auto_Vc_Query(interaction.guild.id)
            if vc_creator_id==0:
                vc_creator='#channel'
            else:
                try:
                    vc_creator=interaction.guild.get_channel(vc_creator_id).mention
                except:
                    vc_creator='#channel'
            Embed.add_field(name='Auto Vc Creator',value=f'> {vc_creator}',inline=False)
            if moderator_roles_ids_list==0:
                roles='@moderator roles'
            else:
                roles=''
                for role_id in moderator_roles_ids_list:
                    try:
                        roles+=f'{interaction.guild.get_role(role_id).mention}, '
                    except:
                        roles+=f'<@&{role_id}>, '
                roles=roles[:-2]
            Embed.add_field(name='Moderator Roles',value=f'> {roles}',inline=False)
            if vc_category_id==0:
                vc_category='#category'
            else:
                try:
                    vc_category=interaction.guild.get_channel(vc_category_id).mention
                except:
                    vc_category='#category'
            Embed.add_field(name='Auto Vc Category',value=f'> {vc_category}',inline=False)
            if member_role_id==0:
                member_role='@role'
            else:
                try:
                    member_role=interaction.guild.get_role(member_role_id).mention
                except:
                    member_role=f'<@&{member_role_id}>'
            Embed.add_field(name='Member Role',value=f'> {member_role}',inline=False)
            view=Auto_Vcs_Menu_View()
            await interaction.response.edit_message(content=None,embed=Embed,view=view)
        elif Choice=='Welcome Message':
            Embed=discord.Embed(title='Welcome Message Settings ⚙️',colour=0x00F3FF)
            channel_id,title,description,colour,activated=Welcome_Message_Query(interaction.guild.id)
            if channel_id==0:
                channel='#channel'
            else:
                try:
                    channel=interaction.guild.get_channel(channel_id).mention
                except:
                    channel='#channel'
            Embed.add_field(name='Welcome Channel',value=f'> {channel}',inline=False)
            Embed.add_field(name='Title',value=f'> {title}',inline=False)
            if description is None:
                description='None'
            Embed.add_field(name='Description',value=f'> {description}',inline=False)
            if colour is None:
                colour='None'
            Embed.add_field(name='Colour',value=f'> #{colour}',inline=False)
            if activated:
                activated='On'
            else:
                activated='Off'
            Embed.add_field(name='Activated',value=f'> {activated}',inline=False)
            view=Welcome_Message_Menu_View()
            await interaction.response.edit_message(content=None,embed=Embed,view=view)

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