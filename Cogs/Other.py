import discord, os, datetime, random
from discord import app_commands
from discord.ext import commands

from Cogs.Auto_Vc import Auto_Vc_Buttons
from DataBase.Welcome_Message import Query as Welcome_Message_Query
from DataBase.Auto_Vc import Remove as Auto_Vc_Remove
from DataBase.Counting import Remove as Counting_Remove

class Other(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot=bot
    @commands.Cog.listener()
    async def on_member_join(self,member):
        Activated=Welcome_Message_Query(member.guild.id,"activated")
        if Activated:
            Welcome_Channel=self.bot.get_channel(Welcome_Message_Query(member.guild.id,"channel_id"))
            Title=Welcome_Message_Query(member.guild.id,"title")
            Description=Welcome_Message_Query(member.guild.id,"description")
            #Colour=hex(int(Welcome_Message_Query(member.guild.id,"colour"),16))
            Colour=discord.Colour.from_str(Welcome_Message_Query(member.guild.id,"colour"))
            Embed=discord.Embed(title=Title,description=Description,color=Colour)
            Embed.set_thumbnail(url=str(member.display_avatar.url))
            Embed.add_field(name="Account Created",value=f"<t:{round(member.created_at.timestamp())}:R>",inline=False)
            Embed.set_footer(text=f"ID: {str(member.id)}")
            Embed.timestamp=datetime.datetime.now()
            await Welcome_Channel.send(embed=Embed)
    @commands.Cog.listener('on_guild_remove')
    async def guild_remove(self,guild:discord.guild):
        Auto_Vc_Remove(guild.id)
        Counting_Remove(guild.id)
    @app_commands.command(name="setup",description="Run this command to set the bot up")
    async def setup(self,interaction:discord.Interaction):
        Embed=discord.Embed(title="Synto Setup ⚙️",description="To configure the bot please use the `/configuration` command. In each section a button labelled ℹ️ will display information about each configurable option.\n\nFor any help/support surrounding the bot, please open a ticket in the [Synto Support Server](https://discord.gg/MdsMmJvaJt)",colour=0x00F3FF)
        Embed.add_field(name="Auto Vc",value="> To setup an auto vc generator, you must select an auto vc creator, an auto vc category and a member role.\n> The command `/control_panel` will send a message which allows members to control their voice channels.",inline=False)
        Embed.add_field(name="Counting",value="> To enable counting, a counting channel needs to be selected in the counting section of the configuration command.",inline=False)
        Embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/dkVKX_iG1FdV8cjqLuEmnz7ZB-5dAyN-kGYRMdnVXbk/%3Fsize%3D4096/https/cdn.discordapp.com/avatars/1160857627631292456/e908335849b2cc5ed76f6e08e31eb2db.png?format=webp&quality=lossless&width=935&height=935")
        await interaction.response.send_message(embed=Embed)
    @app_commands.command(name="control_panel",description="Sends the auto vc control panel")
    async def auto_vc_control_panel(self,interaction:discord.Interaction):
        if interaction.user.guild_permissions.administrator or interaction.user.id==583547084708249602:
            await interaction.response.send_message("setup complete",ephemeral=True)
            Embed=discord.Embed(title="Auto Vc Control Panel",description="You can use this interface to manage your voice channel.",colour=0x00F3FF)
            Embed.set_footer(text="Use the buttons below to manage your voice channel")
            Embed.set_image(url="https://media.discordapp.net/attachments/876226484363202580/1186442888024965180/button_interface_5.png?ex=6593440b&is=6580cf0b&hm=c7f06a4fb2c7f58f87b02f1e0e780944bcaab8ca1def3f8727dcab4e50159633&=&format=webp&quality=lossless&width=532&height=120")
            await interaction.channel.send(embed=Embed,view=Auto_Vc_Buttons())
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this command",ephemeral=True)
    @app_commands.command(name="rps")
    @app_commands.choices(choice=[app_commands.Choice(name="Rock",value="rock"),app_commands.Choice(name="Paper",value="paper"),app_commands.Choice(name="Scissors",value="scissors")])
    async def rps(self,interaction:discord.Interaction,choice:app_commands.Choice[str]):
        Options=["rock","paper","scissors"]
        Bot_Choice=Options[random.randint(0,2)]
        if choice.value==Bot_Choice:
            Result="It's a tie!"
        elif ((choice.value=="rock" and Bot_Choice=="scissors") or
            (choice.value=="paper" and Bot_Choice=="rock") or
            (choice.value=="scissors" and Bot_Choice=="paper")):
            Result="You win!"
        else:
            Result="I win!"
        await interaction.response.send_message(embed=discord.Embed(description=f"You chose {choice.value}\nI chose {Bot_Choice}\n{Result}"))
    @app_commands.command(name="ping",description="Sends the latency of the bot")
    async def ping(self,interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong! Latency: {round(self.bot.latency*1000)}ms",ephemeral=True)
    @app_commands.command(name="bot-info",description="Shows info about the bot")
    async def botinfo(self,interaction:discord.Interaction):
        Uptime_TimeStamp=f"<t:{int(datetime.datetime.timestamp(interaction.client.Time))}:R>"
        Ping=f"{round(interaction.client.latency*1000)}ms"
        Total_Lines=0
        for File in os.listdir("."):
            if os.path.isdir(File):
                for Filename in os.listdir(f"./{File}"):
                    if Filename.endswith(".py"):
                        with open(f"./{File}/{Filename}",'r',encoding='utf-8') as Python_File:
                            Total_Lines+=len(Python_File.readlines())
        if File.endswith(".py"):
            with open(f"./{File}",'r',encoding='utf-8') as Python_File:
                Total_Lines+=len(Python_File.readlines())
        await interaction.response.send_message(embed=discord.Embed(title="Bot Status",description=f"Bot Uptime: {Uptime_TimeStamp}\nLines of code: {Total_Lines}\nPing: {Ping}",color=0x00F3FF),ephemeral=True)
async def setup(bot:commands.Bot):
    await bot.add_cog(Other(bot))