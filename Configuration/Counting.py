import discord

import Checks

import Cogs.Setup as Setup
from DataBase.Counting import Query, Configure, Counting_Channel_Query, Double_Count_Query

class Counting_Menu_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Setup.Select_Menu())
    def Embed(self,interaction):
        Embed=discord.Embed(title='**Counting Settings ⚙️**',colour=0x00F3FF)
        channel_id,double_count=Query(interaction.guild.id)
        if channel_id==0:
            Embed.add_field(name='Counting Channel',value=f'> #channel',inline=False)
        else:
            Embed.add_field(name='Counting Channel',value=f'> {interaction.guild.get_channel(channel_id).mention}',inline=False)
        Embed.add_field(name='Double Count',value=f'> {double_count}',inline=False)
        return Embed
    @discord.ui.button(label='Counting Channel',style=discord.ButtonStyle.grey,row=0,custom_id='counting_channel')
    async def counting_channel(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        view=Counting_Channel_View()
        counting_channel_id,error_message=Counting_Channel_Query(interaction.guild.id)
        if counting_channel_id==0:
            counting_channel='#channel'
        else:
            try:
                counting_channel=interaction.guild.get_channel(counting_channel_id).mention
            except:
                counting_channel='#channel'
        await interaction.response.send_message(embed=discord.Embed(description=f'The Counting Channel is currently set to {counting_channel}',colour=0x00F3FF),ephemeral=True,view=view)
        await view.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label='Double Count',style=discord.ButtonStyle.grey,row=1,custom_id='double_count')
    async def double_count(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        double_count,error_message=Double_Count_Query(interaction.guild.id)
        view=Counting_Double_Count_View()
        await interaction.response.send_message(embed=discord.Embed(description=f'Double Counting is currently set to {double_count}',colour=0x00F3FF),ephemeral=True,view=view)
        await view.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(emoji='ℹ️',style=discord.ButtonStyle.blurple,row=0,custom_id='counting_information')
    async def information(self,interaction:discord.Interaction,button:discord.ui.Button):
        Embed=discord.Embed(title='Counting Settings Information ℹ️',colour=0x00F3FF)
        Embed.add_field(name='Counting Channel',value='> The channel where members can use the bots counting feature.',inline=False)
        Embed.add_field(name='Double Count',value="> True/False: whether a member should be able to count multiple times in a row. True they can, false they can't.",inline=False)
        await interaction.response.send_message(embed=Embed,ephemeral=True)
    @discord.ui.button(emoji='🗑️',style=discord.ButtonStyle.red,row=1,custom_id='counting_delete')
    async def delete(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        await interaction.response.defer()
        await interaction.message.delete()
class Counting_Channel_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Counting_Channel_Select(self))
class Counting_Channel_Select(discord.ui.ChannelSelect):
    def __init__(self,view_self):
        super().__init__(placeholder='Couting Channel',min_values=1,max_values=1,channel_types=[discord.ChannelType.text],custom_id='coutning_channel_select')
        self.view_self=view_self
    async def callback(self,interaction):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        Configure(interaction.guild_id,Channel_id=self.values[0].id)
        await interaction.response.edit_message(embed=discord.Embed(description=f'Successfully set the counting channel to {self.values[0].mention}',colour=0x00F3FF),view=None)
        self.view_self.stop()
class Counting_Double_Count_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(emoji='✅',label='True',style=discord.ButtonStyle.grey,custom_id='double_count_true')
    async def true(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        view=None
        await interaction.response.edit_message(embed=discord.Embed(description='Double Count set to True',colour=0x00F3FF),view=view)
        Configure(interaction.guild_id,Double_Count=True)
        self.stop()
    @discord.ui.button(emoji='❌',label='False',style=discord.ButtonStyle.grey,custom_id='double_count_false')
    async def false(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        view=None
        await interaction.response.edit_message(embed=discord.Embed(description='Double Count set to False',colour=0x00F3FF),view=view)
        Configure(interaction.guild_id,Double_Count=False)
        self.stop()