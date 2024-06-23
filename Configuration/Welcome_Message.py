import discord

import Cogs.Setup as Setup
from DataBase.Welcome_Message import Configure, Query

class Welcome_Message_Menu_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Setup.Select_Menu())
    def Embed(self,interaction):
        Embed=discord.Embed(title="Welcome Message Settings ⚙️",colour=0x00F3FF)
        Channel_id=Query(interaction.guild.id,'channel_id')
        Title=Query(interaction.guild.id,'title')
        Description=Query(interaction.guild.id,'description')
        Colour=Query(interaction.guild.id,'colour')
        Activated=Query(interaction.guild.id,'activated')
        if Channel_id==0:
            Embed.add_field(name="Welcome Channel",value=f"> #channel",inline=False)
        else:
            Embed.add_field(name="Welcome Channel",value=f"> {interaction.guild.get_channel(Channel_id).mention}",inline=False)
        Embed.add_field(name="Title",value=f"> {Title}",inline=False)
        if Description is None:
            Embed.add_field(name="Description",value="> None",inline=False)
        else:
            Embed.add_field(name="Description",value=f"> {Description}",inline=False)
        if Colour is None:
            Embed.add_field(name="Colour",value="> None",inline=False)
        else:
            Embed.add_field(name="Colour",value=f"> #{Colour}",inline=False)
        Embed.add_field(name="Activated",value=f"> {Activated}",inline=False)
        return Embed
    @discord.ui.button(label="Welcome Channel",style=discord.ButtonStyle.grey,row=0,custom_id="welcome_channel")
    async def welcome_channel(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            View=Welcome_Channel_View()
            Channel_id=Query(interaction.guild.id,'channel_id')
            if Channel_id==0:
                await interaction.response.send_message(embed=discord.Embed(description="The Counting Channel is currently set to #channel",colour=0x00F3FF),ephemeral=True,view=View)
            else:
                await interaction.response.send_message(embed=discord.Embed(description=f"The Welcome Channel is currently set to {interaction.guild.get_channel(Channel_id).mention}",colour=0x00F3FF),ephemeral=True,view=View)
            await View.wait()
            await interaction.message.edit(embed=self.Embed(interaction))
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
    @discord.ui.button(label="Title",style=discord.ButtonStyle.grey,row=0,custom_id="welcome_message_title")
    async def title(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            View=Welcome_Message_Title_Modal()
            await interaction.response.send_modal(View)
            await View.wait()
            await interaction.message.edit(embed=self.Embed(interaction))
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
    @discord.ui.button(label="Description",style=discord.ButtonStyle.grey,row=1,custom_id="welcome_message_description")
    async def description(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            View=Welcome_Message_Description_Modal()
            await interaction.response.send_modal(View)
            await View.wait()
            await interaction.message.edit(embed=self.Embed(interaction))
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
    @discord.ui.button(label="Colour",style=discord.ButtonStyle.grey,row=1,custom_id="welcome_message_colour")
    async def colour(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            View=Welcome_Message_Colour_Modal()
            await interaction.response.send_modal(View)
            await View.wait()
            await interaction.message.edit(embed=self.Embed(interaction))
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
    @discord.ui.button(emoji="ℹ️",style=discord.ButtonStyle.blurple,row=0,custom_id="welcome_message_information")
    async def information(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            Embed=discord.Embed(title="Welcome Message Settings Information ℹ️",colour=0x00F3FF)
            Embed.add_field(name="Welcome Channel",value="> The channel where the welcome message will be sent if the feature is turned on.",inline=False)
            Embed.add_field(name="Title",value="> The title of the welcome message.",inline=False)
            Embed.add_field(name="Description",value="> The description of the welcome message. The description can contain a mention of the person who has just joined the server. Include the following within the description to mention the user: {member.mention}",inline=False)
            Embed.add_field(name="Colour",value="> The colour of the welcome message embed. A new colour should be entered as the 6 digit part of a colour hex code. For example for the colour red, you would enter: FF0000",inline=False)
            Embed.add_field(name="Activated",value="> Whether the welcome message functionality should be turned on or off.",inline=False)
            await interaction.response.send_message(embed=Embed,ephemeral=True)
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
    @discord.ui.button(emoji="🗑️",style=discord.ButtonStyle.red,row=1,custom_id="welcome_message_delete")
    async def delete(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            await interaction.response.defer()
            await interaction.message.delete()
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
    @discord.ui.button(label="Activated",style=discord.ButtonStyle.grey,row=2,custom_id="welcome_message_activated")
    async def activated(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            View=Welcome_Message_Activated_View()
            Activated=Query(interaction.guild.id,'activated')
            if Activated:
                Activated="On"
            else:
                Activated="Off"
            await interaction.response.send_message(embed=discord.Embed(description=f"The welcome message functionality is currently turned {Activated}",colour=0x00F3FF),ephemeral=True,view=View)
            await View.wait()
            await interaction.message.edit(embed=self.Embed(interaction))
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
class Welcome_Channel_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Welcome_Channel_Select(self))
class Welcome_Channel_Select(discord.ui.ChannelSelect):
    def __init__(self,View_Self):
        super().__init__(placeholder="Welcome Channel",min_values=1,max_values=1,channel_types=[discord.ChannelType.text],custom_id="welcome_channel_select")
        self.View_Self=View_Self
    async def callback(self,interaction):
        if interaction.user.guild_permissions.administrator:
            Configure(interaction.guild_id,Channel_id=self.values[0].id)
            await interaction.response.edit_message(embed=discord.Embed(description=f"Successfully set the welcome channel to {self.values[0].mention}",colour=0x00F3FF),view=None)
            self.View_Self.stop()
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this command",ephemeral=True)
class Welcome_Message_Title_Modal(discord.ui.Modal,title="Welcome Message Title"):
    Title=discord.ui.TextInput(label="Enter your new welcome message title",style=discord.TextStyle.short,required=True)
    async def on_submit(self,interaction:discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(embed=discord.Embed(description="The welcome message title has been updated:\n"+str(self.Title),colour=0x00F3FF),ephemeral=True)
            Configure(interaction.guild_id,Title=self.Title)
            self.stop()
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
            self.stop()
class Welcome_Message_Description_Modal(discord.ui.Modal,title="Welcome Message Description"):
    Description=discord.ui.TextInput(label="Enter your new welcome message description",style=discord.TextStyle.long,required=False)
    async def on_submit(self,interaction:discord.Interaction):
        print(self.Description)
        if interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(embed=discord.Embed(description="The welcome message description has been updated to:\n"+str(self.Description),colour=0x00F3FF),ephemeral=True)
            Configure(interaction.guild_id,Description=self.Description)
            self.stop()
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
            self.stop()
class Welcome_Message_Colour_Modal(discord.ui.Modal,title="Welcome Message Colour"):
    Colour=discord.ui.TextInput(label="Enter your new welcome message colour",style=discord.TextStyle.short,required=True)
    async def on_submit(self,interaction:discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(embed=discord.Embed(description=f"The welcome message colour has been updated to:\n{self.Colour}",colour=0x00F3FF),ephemeral=True)
            Configure(interaction.guild_id,Colour=self.Colour)
            self.stop()
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
            self.stop()
class Welcome_Message_Activated_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(emoji="✅",label="On",style=discord.ButtonStyle.grey,custom_id="welcome_channel_true")
    async def true(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            View=None
            await interaction.response.edit_message(embed=discord.Embed(description="The welcome message functionality has been turned on",colour=0x00F3FF),view=View)
            Configure(interaction.guild_id,Activated=True)
            self.stop()
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
    @discord.ui.button(emoji="❌",label="Off",style=discord.ButtonStyle.grey,custom_id="welcome_channel_false")
    async def false(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            View=None
            await interaction.response.edit_message(embed=discord.Embed(description="The welcome message functionality has been turned off",colour=0x00F3FF),view=View)
            Configure(interaction.guild_id,Activated=False)
            self.stop()
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)