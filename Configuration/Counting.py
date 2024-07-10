import discord

import Cogs.Setup as Setup
from DataBase.Counting import Configure, Query

class Counting_Menu_View(discord.ui.View):
    def __init__(self,Connection=None):
        super().__init__(timeout=None)
        self.add_item(Setup.Select_Menu())
        self.Connection=Connection
    def Embed(self,interaction):
        Embed=discord.Embed(title="**Counting Settings ⚙️**",colour=0x00F3FF)
        Channel_id=Query(interaction.guild.id,'channel_id',Connection=self.Connection)
        Double_Count=Query(interaction.guild.id,'double_count',Connection=self.Connection)
        if Channel_id==0:
            Embed.add_field(name="Counting Channel",value=f"> #channel",inline=False)
        else:
            Embed.add_field(name="Counting Channel",value=f"> {interaction.guild.get_channel(Channel_id).mention}",inline=False)
        Embed.add_field(name="Double Count",value=f"> {Double_Count}",inline=False)
        return Embed
    @discord.ui.button(label="Counting Channel",style=discord.ButtonStyle.grey,row=0,custom_id="counting_channel")
    async def counting_channel(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            View=Counting_Channel_View(self.Connection)
            try:
                await interaction.response.send_message(embed=discord.Embed(description=f"The Counting Channel is currently set to {interaction.guild.get_channel(Query(interaction.guild.id,'channel_id',Connection=self.Connection)).mention}",colour=0x00F3FF),ephemeral=True,view=View)
            except:
                Configure(interaction.guild.id,Connection=self.Connection)
                await interaction.response.send_message(embed=discord.Embed(description="The Counting Channel is currently set to #channel",colour=0x00F3FF),ephemeral=True,view=View)
            await View.wait()
            await interaction.message.edit(embed=self.Embed(interaction))
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
    @discord.ui.button(label="Double Count",style=discord.ButtonStyle.grey,row=1,custom_id="double_count")
    async def double_count(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            View=Counting_Double_Count_View(self.Connection)
            await interaction.response.send_message(embed=discord.Embed(description=f"Double Counting is currently set to {Query(interaction.guild.id,'double_count',Connection=self.Connection)}",colour=0x00F3FF),ephemeral=True,view=View)
            await View.wait()
            await interaction.message.edit(embed=self.Embed(interaction))
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
    @discord.ui.button(emoji="ℹ️",style=discord.ButtonStyle.blurple,row=0,custom_id="counting_information")
    async def information(self,interaction:discord.Interaction,button:discord.ui.Button):
        Embed=discord.Embed(title="Counting Settings Information ℹ️",colour=0x00F3FF)
        Embed.add_field(name="Counting Channel",value="> The channel where members can use the bots counting feature.",inline=False)
        Embed.add_field(name="Double Count",value="> True/False: whether a member should be able to count multiple times in a row. True they can, false they can't.",inline=False)
        await interaction.response.send_message(embed=Embed,ephemeral=True)
    @discord.ui.button(emoji="🗑️",style=discord.ButtonStyle.red,row=1,custom_id="counting_delete")
    async def delete(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            await interaction.response.defer()
            await interaction.message.delete()
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
class Counting_Channel_View(discord.ui.View):
    def __init__(self,Connection=None):
        super().__init__(timeout=None)
        self.add_item(Counting_Channel_Select(self,Connection))
class Counting_Channel_Select(discord.ui.ChannelSelect):
    def __init__(self,View_Self,Connection):
        super().__init__(placeholder="Couting Channel",min_values=1,max_values=1,channel_types=[discord.ChannelType.text],custom_id="coutning_channel_select")
        self.View_Self=View_Self
        self.Connection=Connection
    async def callback(self,interaction):
        if interaction.user.guild_permissions.administrator:
            Configure(interaction.guild_id,Channel_id=self.values[0].id,Connection=self.Connection)
            await interaction.response.edit_message(embed=discord.Embed(description=f"Successfully set the counting channel to {self.values[0].mention}",colour=0x00F3FF),view=None)
            self.View_Self.stop()
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this command",ephemeral=True)
class Counting_Double_Count_View(discord.ui.View):
    def __init__(self,Connection=None):
        super().__init__(timeout=None)
        self.Connection=Connection
    @discord.ui.button(emoji="✅",label="True",style=discord.ButtonStyle.grey,custom_id="double_count_true")
    async def true(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            View=None
            await interaction.response.edit_message(embed=discord.Embed(description="Double Count set to True",colour=0x00F3FF),view=View)
            Configure(interaction.guild_id,Double_Count=True,Connection=self.Connection)
            self.stop()
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
    @discord.ui.button(emoji="❌",label="False",style=discord.ButtonStyle.grey,custom_id="double_count_false")
    async def false(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            View=None
            await interaction.response.edit_message(embed=discord.Embed(description="Double Count set to False",colour=0x00F3FF),view=View)
            Configure(interaction.guild_id,Double_Count=False,Connection=self.Connection)
            self.stop()
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)