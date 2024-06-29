import discord, os, datetime, random
from discord import app_commands
from discord.ext import commands

from Cogs.Auto_Vc import Auto_Vc_Buttons
from DataBase.Welcome_Message import Query as Welcome_Message_Query
from DataBase.Auto_Vc import Remove as Auto_Vc_Remove
from DataBase.Counting import Remove as Counting_Remove
from DataBase.Welcome_Message import Configure as Welcome_Message_Configure, Remove as Welcome_Message_Remove

class Other(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot=bot
    @commands.Cog.listener()
    async def on_member_join(self,member):
        Welcome_Message_Configure(member.guild.id)
        Activated=Welcome_Message_Query(member.guild.id,"activated")
        if Activated:
            Welcome_Channel=self.bot.get_channel(Welcome_Message_Query(member.guild.id,"channel_id"))
            if Welcome_Channel==None:
                return
            Title=Welcome_Message_Query(member.guild.id,"title")
            Description=Welcome_Message_Query(member.guild.id,"description")
            if Description=="None":
                Description=None
            elif "{member.mention}" in Description:
                Position=Description.index("{member.mention}")
                Description=f"{Description[:Position]}{member.mention}{Description[Position+16:]}"
            Colour=Welcome_Message_Query(member.guild.id,"colour")
            if Colour=="None":
                Colour="000000"
            elif Colour[:1]=="#":
                Colour=Colour[1:]
                Welcome_Message_Configure(member.guild.id,Colour=Colour)
            try:
                Colour=discord.Colour.from_str("#"+Colour)
            except:
                Colour="000000"
            Embed=discord.Embed(title=f"{Title}",description=Description,color=Colour)
            Embed.set_thumbnail(url=str(member.display_avatar.url))
            Embed.add_field(name="Account Created",value=f"<t:{round(member.created_at.timestamp())}:R>",inline=False)
            Embed.set_footer(text=f"ID: {str(member.id)}")
            Embed.timestamp=datetime.datetime.now()
            await Welcome_Channel.send(embed=Embed)
    @commands.Cog.listener('on_guild_remove')
    async def guild_remove(self,guild:discord.guild):
        Auto_Vc_Remove(guild.id)
        Counting_Remove(guild.id)
        Welcome_Message_Remove(guild.id)
    @app_commands.command(name="setup",description="Run this command to set the bot up")
    async def setup(self,interaction:discord.Interaction):
        Embed=discord.Embed(title="Synto Setup ⚙️",description="To configure the bot please use the `/configuration` command. In each section a button labelled ℹ️ will display information about each configurable option.\n\nFor any help/support surrounding the bot, please open a ticket in the [Synto Support Server](https://discord.gg/MdsMmJvaJt)",colour=0x00F3FF)
        Embed.add_field(name="Auto Vc",value="> To setup an auto vc generator, you must select an auto vc creator, category and a member role within the configuration command.\n> The command `/control_panel` will send a message which allows members to control their voice channels.",inline=False)
        Embed.add_field(name="Counting",value="> To enable counting, a counting channel needs to be selected within the configuration command.",inline=False)
        Embed.add_field(name="Welcome Message",value="> To enable the welcome message functionality, a welcome channel needs to be and the feature needs to be activated from within the configuration command.")
        Embed.set_thumbnail(url="https://media.discordapp.net/attachments/1166916938530816018/1254624501115912223/Synto_Profile.png?ex=667a2b9e&is=6678da1e&hm=061315c8fecb685fa44cccb2611a01f5567d40d5dd7db1f93a21e3986c669516&=&format=webp&quality=lossless&width=437&height=437")
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