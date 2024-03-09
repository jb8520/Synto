import discord, os

import Cogs.Setup as Setup
from DataBase.Auto_Vc import Configure, Query

from dotenv import load_dotenv
load_dotenv()

class Auto_Vcs_Menu_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Setup.Select_Menu())
    def Embed(self,interaction):
        Embed=discord.Embed(title="Auto Voice Channel Settings ⚙️",colour=0x00F3FF)
        Vc_Creator_id=Query(interaction.guild.id,'vc_creator_id')
        Vc_Category_id=Query(interaction.guild.id,'vc_category_id')
        Member_Role=Query(interaction.guild.id,'member_role')
        Bypass_Roles=Query(interaction.guild.id,'bypass_roles')
        if Vc_Creator_id==0:
            Embed.add_field(name="Auto Vc Creator",value=f"> #channel",inline=False)
        else:
            Embed.add_field(name="Auto Vc Creator",value=f"> {interaction.guild.get_channel(Query(interaction.guild.id,'vc_creator_id')).mention}",inline=False)
        if Bypass_Roles==0:
            Embed.add_field(name="Moderator Roles",value=f"> @moderator roles",inline=False)
        else:
            Roles=""
            for Role_id in Query(interaction.guild.id,'bypass_roles'):
                Roles+=f"{interaction.guild.get_role(Role_id).mention}, "
            Roles=Roles[:-2]
            Embed.add_field(name="Moderator Roles",value=f"> {Roles}",inline=False)
        if Vc_Category_id==0:
            Embed.add_field(name="Auto Vc Category",value=f"> #category",inline=False)
        else:
            Embed.add_field(name="Auto Vc Category",value=f"> {interaction.guild.get_channel(Query(interaction.guild.id,'vc_category_id')).mention}",inline=False)
        if Member_Role==0:
            Embed.add_field(name="Member Role",value=f"> @role",inline=False)
        else:
            Embed.add_field(name="Member Role",value=f"> {interaction.guild.get_role(Query(interaction.guild.id,'member_role')).mention}",inline=False)
        return Embed
    @discord.ui.button(label="Vc Creator",style=discord.ButtonStyle.grey,row=0,custom_id="vc_creator")
    async def vc_creator(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            Vc_Creator_id=Query(interaction.guild.id,'vc_creator_id')
            if Vc_Creator_id!=0:
                Channel=interaction.guild.get_channel(Vc_Creator_id).mention
            else:
                Channel="#channel"
            View=Vc_Creator_View()
            await interaction.response.send_message(embed=discord.Embed(description=f"The Auto Vc Creator is currently set to {Channel}",colour=0x00F3FF),ephemeral=True,view=View)
            await View.wait()
            await interaction.message.edit(embed=self.Embed(interaction),view=Auto_Vcs_Menu_View())
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
    @discord.ui.button(label="Moderator Roles",style=discord.ButtonStyle.grey,row=0,custom_id="bypass_roles")
    async def bypass_roles(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            Bypass_Roles=Query(interaction.guild.id,'bypass_roles')
            if Bypass_Roles!=0:
                Roles=""
                for Role_id in Bypass_Roles:
                    Roles+=f"{interaction.guild.get_role(Role_id).mention}, "
                Roles=Roles[:-2]
            else:                
                Roles="@moderator roles"
            View=Bypass_Roles_View()
            await interaction.response.send_message(embed=discord.Embed(description=f"The Moderator Roles are currently set as: {Roles}",colour=0x00F3FF),ephemeral=True,view=View)
            await View.wait()
            await interaction.message.edit(embed=self.Embed(interaction),view=Auto_Vcs_Menu_View())
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
    @discord.ui.button(label="Vc Category",style=discord.ButtonStyle.grey,row=1,custom_id="vc_category")
    async def vc_Category(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            Vc_Category_id=Query(interaction.guild.id,'vc_category_id')
            if Vc_Category_id!=0:
                Category=interaction.guild.get_channel(Vc_Category_id).mention
            else:
                Category="#category"
            View=Vc_Category_View()
            await interaction.response.send_message(embed=discord.Embed(description=f"The Auto Vc Category is currently set to {Category}",colour=0x00F3FF),ephemeral=True,view=View)
            await View.wait()
            await interaction.message.edit(embed=self.Embed(interaction),view=Auto_Vcs_Menu_View())
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
    @discord.ui.button(label="Member Role",style=discord.ButtonStyle.grey,row=1,custom_id="member_role")
    async def member_role(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            Member_Role=Query(interaction.guild.id,'member_role')
            if Member_Role!=0:
                Role=interaction.guild.get_role(Member_Role).mention
            else:
                Role="#role"
            View=Member_Role_View()
            await interaction.response.send_message(embed=discord.Embed(description=f"The Member Role is currently set to {Role}",colour=0x00F3FF),ephemeral=True,view=View)
            await View.wait()
            await interaction.message.edit(embed=self.Embed(interaction),view=Auto_Vcs_Menu_View())
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
    @discord.ui.button(emoji="ℹ️",style=discord.ButtonStyle.blurple,row=0,custom_id="auto_vc_information")
    async def information(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            Embed=discord.Embed(title="Auto Voice Channel Settings Information ℹ️",colour=0x00F3FF)
            Embed.add_field(name="Auto Vc Creator",value="> The permanent channel that will be used to create a new temporary voice channel",inline=False)
            Embed.add_field(name="Moderator Roles",value="> The roles which will always be able to access any created voice channels, regardless if it is hidden/locked",inline=False)
            Embed.add_field(name="Auto Vc Category",value="> The category in which the created voice channels will be located in",inline=False)
            Embed.add_field(name="Member Role",value="> This should be the role that by default can access created voice channels",inline=False)
            await interaction.response.send_message(embed=Embed,ephemeral=True)
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)
    @discord.ui.button(emoji="🗑️",style=discord.ButtonStyle.red,row=1,custom_id="auto_vc_delete")
    async def delete(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            await interaction.response.defer()
            await interaction.message.delete()
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this button",ephemeral=True)

class Vc_Creator_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Vc_Creator_Select(self))
class Vc_Creator_Select(discord.ui.ChannelSelect):
    def __init__(self,View_Self):
        super().__init__(placeholder="Vc Creator",min_values=1,max_values=1,channel_types=[discord.ChannelType.voice],custom_id="vc_creator_select")
        self.View_Self=View_Self
    async def callback(self,interaction):
        if interaction.user.guild_permissions.administrator:
            Configure(interaction.guild_id,Vc_Creator_id=self.values[0].id)
            await interaction.response.edit_message(embed=discord.Embed(description=f"Successfully set the auto vc creator channel to {self.values[0].mention}",colour=0x00F3FF),view=None)
            self.View_Self.stop()
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this command",ephemeral=True)

class Vc_Category_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Vc_Category_Select(self))
class Vc_Category_Select(discord.ui.ChannelSelect):
    def __init__(self,View_Self):
        super().__init__(placeholder="Auto Vc Category",min_values=1,max_values=1,channel_types=[discord.ChannelType.category],custom_id="vc_category_select")
        self.View_Self=View_Self
    async def callback(self,interaction):
        if interaction.user.guild_permissions.administrator:
            Vc_Category_id=Query(interaction.guild.id,'vc_category_id')
            if Vc_Category_id!=0:
                try:
                    Category=interaction.guild.get_channel(Vc_Category_id)
                    await Category.set_permissions(interaction.guild.get_member(os.environ["BOT_ID"]),overwrite=None)
                except:
                    Error=True
            New_Category=interaction.guild.get_channel(self.values[0].id)
            Configure(interaction.guild_id,Vc_Category_id=New_Category.id)
            await interaction.response.edit_message(embed=discord.Embed(description=f"Successfully set the auto vc category to {New_Category.mention}",colour=0x00F3FF),view=None)
            overwrite=discord.PermissionOverwrite(view_channel=True,manage_channels=True,manage_permissions=True,manage_roles=True)
            await New_Category.set_permissions(interaction.guild.get_member(os.environ["BOT_ID"]),overwrite=overwrite)
            self.View_Self.stop()
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this command",ephemeral=True)

class Member_Role_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Member_Role_Select(self))
class Member_Role_Select(discord.ui.RoleSelect):
    def __init__(self,View_Self):
        super().__init__(placeholder="Member Role",min_values=1,max_values=1,custom_id="member_role_select")
        self.View_Self=View_Self
    async def callback(self,interaction):
        if interaction.user.guild_permissions.administrator:
            Configure(interaction.guild_id,Member_Role=self.values[0].id)
            await interaction.response.edit_message(embed=discord.Embed(description=f"Successfully set the member role to {self.values[0].mention}",colour=0x00F3FF),view=None)
            self.View_Self.stop()
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this command",ephemeral=True)

class Bypass_Roles_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Bypass_Roles_Select(self))
class Bypass_Roles_Select(discord.ui.RoleSelect):
    def __init__(self,View_Self):
        super().__init__(placeholder="Moderator Roles",min_values=1,max_values=25,custom_id="bypass_roles_select")
        self.View_Self=View_Self
    async def callback(self,interaction):
        if interaction.user.guild_permissions.administrator:
            ids=[]
            Roles=""
            for Role in self.values:
                ids.append(Role.id)
                Roles+=f"{Role.mention}, "
            Roles=Roles[:-2]
            Configure(interaction.guild_id,Bypass_Roles=ids)
            await interaction.response.edit_message(embed=discord.Embed(description=f"Successfully set the moderator roles: {Roles}",colour=0x00F3FF),view=None)
            self.View_Self.stop()
        else:
            await interaction.response.send_message("❌ You need to have the administrator permission to use this command",ephemeral=True)