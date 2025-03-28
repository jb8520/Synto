import discord

import Checks

import Cogs.Setup as Setup
from DataBase.Welcome_Message import Configure, Query, Welcome_Channel_Query, Activated_Query

class Welcome_Message_Menu_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Setup.Select_Menu())
    def Embed(self,interaction):
        Embed=discord.Embed(title='Welcome Message Settings ⚙️',colour=0x00F3FF)
        channel_id,title,description,colour,activated=Query(interaction.guild.id)
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
        return Embed
    @discord.ui.button(label='Welcome Channel',style=discord.ButtonStyle.grey,row=0,custom_id='welcome_channel')
    async def welcome_channel(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        view=Welcome_Channel_View()
        welcome_channel_id,error_message=Welcome_Channel_Query(interaction.guild.id)
        if welcome_channel_id==0:
            welcome_channel='#channel'
        else:
            try:
                welcome_channel=interaction.guild.get_channel(welcome_channel_id).mention
            except:
                welcome_channel='#channel'
        await interaction.response.send_message(embed=discord.Embed(description=f'The Welcome Channel is currently set to {welcome_channel}',colour=0x00F3FF),ephemeral=True,view=view)
        await view.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label='Title',style=discord.ButtonStyle.grey,row=0,custom_id='welcome_message_title')
    async def title(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        View=Welcome_Message_Title_Modal()
        await interaction.response.send_modal(View)
        await View.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label='Description',style=discord.ButtonStyle.grey,row=1,custom_id='welcome_message_description')
    async def description(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        View=Welcome_Message_Description_Modal()
        await interaction.response.send_modal(View)
        await View.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label='Colour',style=discord.ButtonStyle.grey,row=1,custom_id='welcome_message_colour')
    async def colour(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        View=Welcome_Message_Colour_Modal()
        await interaction.response.send_modal(View)
        await View.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(emoji='ℹ️',style=discord.ButtonStyle.blurple,row=0,custom_id='welcome_message_information')
    async def information(self,interaction:discord.Interaction,button:discord.ui.Button):
        Embed=discord.Embed(title='Welcome Message Settings Information ℹ️',colour=0x00F3FF)
        Embed.add_field(name='Welcome Channel',value='> The channel where the welcome message will be sent if the feature is turned on.',inline=False)
        Embed.add_field(name='Title',value='> The title of the welcome message.',inline=False)
        Embed.add_field(name='Description',value='> The description of the welcome message. The description can contain a mention of the person who has just joined the server. Include the following within the description to mention the user: member.mention',inline=False)
        Embed.add_field(name='Colour',value='> The colour of the welcome message embed. A new colour should be entered as the 6 digit part of a colour hex code. For example for the colour red, you would enter: FF0000',inline=False)
        Embed.add_field(name='Activated',value='> Whether the welcome message functionality should be turned on or off.',inline=False)
        await interaction.response.send_message(embed=Embed,ephemeral=True)
    @discord.ui.button(emoji='🗑️',style=discord.ButtonStyle.red,row=1,custom_id='welcome_message_delete')
    async def delete(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        await interaction.response.defer()
        await interaction.message.delete()
    @discord.ui.button(label='Activated',style=discord.ButtonStyle.grey,row=2,custom_id='welcome_message_activated')
    async def activated(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        View=Welcome_Message_Activated_View()
        Activated=Activated_Query(interaction.guild.id)
        if Activated:
            Activated='On'
        else:
            Activated='Off'
        await interaction.response.send_message(embed=discord.Embed(description=f'The welcome message functionality is currently turned {Activated}',colour=0x00F3FF),ephemeral=True,view=View)
        await View.wait()
        await interaction.message.edit(embed=self.Embed(interaction))

class Welcome_Channel_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Welcome_Channel_Select(self))
class Welcome_Channel_Select(discord.ui.ChannelSelect):
    def __init__(self,View_Self):
        super().__init__(placeholder='Welcome Channel',min_values=1,max_values=1,channel_types=[discord.ChannelType.text],custom_id='welcome_channel_select')
        self.View_Self=View_Self
    async def callback(self,interaction):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        Configure(interaction.guild_id,channel_id=self.values[0].id)
        await interaction.response.edit_message(embed=discord.Embed(description=f'Successfully set the welcome channel to {self.values[0].mention}',colour=0x00F3FF),view=None)
        self.View_Self.stop()

class Welcome_Message_Title_Modal(discord.ui.Modal,title='Welcome Message Title'):
    Title=discord.ui.TextInput(label='Enter your new welcome message title',style=discord.TextStyle.short,required=True)
    async def on_submit(self,interaction:discord.Interaction):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            self.stop()
            return
        await interaction.response.send_message(embed=discord.Embed(description='The welcome message title has been updated:\n'+str(self.Title),colour=0x00F3FF),ephemeral=True)
        Configure(interaction.guild_id,title=self.Title)
        self.stop()

class Welcome_Message_Description_Modal(discord.ui.Modal,title='Welcome Message Description'):
    Description=discord.ui.TextInput(label='Enter your new welcome message description',placeholder='Enter None to remove the description',style=discord.TextStyle.long,required=True)
    async def on_submit(self,interaction:discord.Interaction):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            self.stop()
            return
        await interaction.response.send_message(embed=discord.Embed(description='The welcome message description has been updated to:\n'+str(self.Description),colour=0x00F3FF),ephemeral=True)
        if str(self.Description).lower()=='none':
            self.Description='None'
        Configure(interaction.guild_id,description=self.Description)
        self.stop()

class Welcome_Message_Colour_Modal(discord.ui.Modal,title='Welcome Message Colour'):
    Colour=discord.ui.TextInput(label='Enter your new welcome message colour',placeholder='Enter None to remove the colour',style=discord.TextStyle.short,required=True)
    async def on_submit(self,interaction:discord.Interaction):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            self.stop()
            return
        colour=str(self.Colour)
        if colour[:1]=='#':
            colour=colour[1:]
        try:
            if colour.lower()=='none':
                colour='None'
            else:
                discord.Colour.from_str('#'+colour)
        except:
            await interaction.response.send_message(f'❌ The inputted colour ({self.Colour}) is not in the accepted form (the 6 digit part of a colour hex code). The welcome message colour is unchanged.',ephemeral=True)
        else:
            await interaction.response.send_message(embed=discord.Embed(description=f'The welcome message colour has been updated to:\n{colour}',colour=0x00F3FF),ephemeral=True)
            Configure(interaction.guild_id,colour=colour)
        finally:
            self.stop()                

class Welcome_Message_Activated_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(emoji='✅',label='On',style=discord.ButtonStyle.grey,custom_id='welcome_channel_true')
    async def true(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        View=None
        await interaction.response.edit_message(embed=discord.Embed(description='The welcome message functionality has been turned on',colour=0x00F3FF),view=View)
        Configure(interaction.guild_id,activated=True)
        self.stop()
    @discord.ui.button(emoji='❌',label='Off',style=discord.ButtonStyle.grey,custom_id='welcome_channel_false')
    async def false(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        View=None
        await interaction.response.edit_message(embed=discord.Embed(description='The welcome message functionality has been turned off',colour=0x00F3FF),view=View)
        Configure(interaction.guild_id,activated=False)
        self.stop()