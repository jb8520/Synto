import discord

from discord import app_commands
from discord.ext import commands

import os, datetime, random

import Checks


from Cogs.Auto_Vc import Auto_Vc_Buttons
from DataBase.Welcome_Message import Query as Welcome_Message_Query, Configure as Welcome_Message_Configure
from DataBase.Auto_Vc import Remove_Server as Auto_Vc_Remove_Server
from DataBase.Counting import Remove_Server as Counting_Remove_Server
from DataBase.Welcome_Message import Remove_Server as Welcome_Message_Remove_Server

class Other(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot=bot
    
    # welcome message listener
    @commands.Cog.listener()
    async def on_member_join(self,member):
        Welcome_Message_Configure(member.guild.id)
        channel_id,title,description,colour,activated=Welcome_Message_Query(member.guild.id)
        if activated:
            welcome_channel=self.bot.get_channel(channel_id)
            if welcome_channel==None:
                return
            if description=='None':
                description=None
            elif 'member.mention' in description:
                position=description.index('member.mention')
                description=f'{description[:position]}{member.mention}{description[position+14:]}'
            if colour=='None':
                colour='000000'
            elif colour[:1]=='#':
                colour=colour[1:]
                #change to welcome message update
                Welcome_Message_Configure(member.guild.id,Colour=colour)
            try:
                colour=discord.Colour.from_str('#'+colour)
            except:
                colour='#000000'
            Embed=discord.Embed(title=f'{title}',description=description,color=colour)
            Embed.set_thumbnail(url=str(member.display_avatar.url))
            Embed.add_field(name='Account Created',value=f'<t:{round(member.created_at.timestamp())}:R>',inline=False)
            Embed.set_footer(text=f'ID: {str(member.id)}')
            Embed.timestamp=datetime.datetime.now()
            await welcome_channel.send(embed=Embed)
    
    # remove a server from the database when the bot leaves that server
    @commands.Cog.listener('on_guild_remove')
    async def guild_remove(self,guild:discord.guild):
        Auto_Vc_Remove_Server(guild.id)
        Counting_Remove_Server(guild.id)
        Welcome_Message_Remove_Server(guild.id)
    
    # sends an embed showing the user how to set the bot up
    @app_commands.command(name='setup',description='Run this command to set the bot up')
    async def setup(self,interaction:discord.Interaction):
        Embed=discord.Embed(title='Synto Setup ⚙️',description='To configure the bot please use the `/configuration` command. In each section a button labelled ℹ️ will display information about each configurable option.\n\nFor any help/support surrounding the bot, please open a ticket in the [Synto Support Server](https://discord.gg/MdsMmJvaJt)',colour=0x00F3FF)
        Embed.add_field(name='Auto Vc',value='> To setup an auto vc generator, you must select an auto vc creator, category and a member role within the configuration command.\n> The command `/control_panel` will send a message which allows members to control their voice channels.',inline=False)
        Embed.add_field(name='Counting',value='> To enable counting, a counting channel needs to be selected within the configuration command.',inline=False)
        Embed.add_field(name='Welcome Message',value='> To enable the welcome message functionality, a welcome channel needs to be selected and the feature needs to be activated from within the configuration command.')
        Embed.set_thumbnail(url='https://media.discordapp.net/attachments/1166916938530816018/1254624501115912223/Synto_Profile.png?ex=667a2b9e&is=6678da1e&hm=061315c8fecb685fa44cccb2611a01f5567d40d5dd7db1f93a21e3986c669516&=&format=webp&quality=lossless&width=437&height=437')
        await interaction.response.send_message(embed=Embed)
    
    # sends the auto vc control panel message
    @app_commands.command(name='control_panel',description='Sends the auto vc control panel')
    async def auto_vc_control_panel(self,interaction:discord.Interaction):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        await interaction.response.send_message('setup complete',ephemeral=True)
        Embed=discord.Embed(title='Auto Vc Control Panel',description='You can use this interface to manage your voice channel.',colour=0x00F3FF)
        Embed.set_footer(text='Use the buttons below to manage your voice channel')
        Embed.set_image(url='https://media.discordapp.net/attachments/876226484363202580/1186442888024965180/button_interface_5.png?ex=6593440b&is=6580cf0b&hm=c7f06a4fb2c7f58f87b02f1e0e780944bcaab8ca1def3f8727dcab4e50159633&=&format=webp&quality=lossless&width=532&height=120')
        await interaction.channel.send(embed=Embed,view=Auto_Vc_Buttons())
    
    #rock paper scissors game
    @app_commands.command(name='rps')
    @app_commands.choices(choice=[app_commands.Choice(name='Rock',value='rock'),app_commands.Choice(name='Paper',value='paper'),app_commands.Choice(name='Scissors',value='scissors')])
    async def rps(self,interaction:discord.Interaction,choice:app_commands.Choice[str]):
        options=['rock','paper','scissors']
        bot_choice=options[random.randint(0,2)]
        if choice.value==bot_choice:
            result='It\'s a tie!'
        elif ((choice.value=='rock' and bot_choice=='scissors') or
            (choice.value=='paper' and bot_choice=='rock') or
            (choice.value=='scissors' and bot_choice=='paper')):
            result='You win!'
        else:
            result='I win!'
        await interaction.response.send_message(embed=discord.Embed(description=f'You chose {choice.value}\nI chose {bot_choice}\n{result}'))
    
    # sends the latency of the bot
    @app_commands.command(name='ping',description='Sends the latency of the bot')
    async def ping(self,interaction: discord.Interaction):
        await interaction.response.send_message(f'Pong! Latency: {round(self.bot.latency*1000)}ms',ephemeral=True)
    
    #sends info about the bot
    @app_commands.command(name='bot-info',description='Shows info about the bot')
    async def botinfo(self,interaction:discord.Interaction):
        uptime_timestamp=f'<t:{int(datetime.datetime.timestamp(interaction.client.time))}:R>'
        ping=f'{round(interaction.client.latency*1000)}ms'
        total_lines=0
        file_list=[]
        for item in os.listdir('.'):
            if item.endswith('.py'):
                file=item
                file_list.append(f'./{file}')
            elif os.path.isdir(item):
                folder=item
                for file in os.listdir(f'./{item}'):
                    if file.endswith('.py'):
                        file_list.append(f'./{folder}/{file}')
        for file in file_list:
            with open(file,'r',encoding='utf-8') as opened_file:
                total_lines+=len(opened_file.readlines())
        await interaction.response.send_message(embed=discord.Embed(title='Bot Status',description=f'Bot Uptime: {uptime_timestamp}\nLines of code: {total_lines}\nPing: {ping}',color=0x00F3FF),ephemeral=True)


async def setup(bot:commands.Bot):
    await bot.add_cog(Other(bot))