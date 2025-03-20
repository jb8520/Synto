import discord

import Checks

import Cogs.Setup as Setup
from DataBase.Auto_Vc import Query, Configure, Vc_Creator_Query, Vc_Category_Query, Member_Role_Query, Moderator_Roles_Query

from dotenv import load_dotenv
load_dotenv()

class Auto_Vcs_Menu_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Setup.Select_Menu())
    def Embed(self,interaction):
        Embed=discord.Embed(title="Auto Voice Channel Settings ⚙️",colour=0x00F3FF)
        vc_creator_id,vc_category_id,member_role_id,moderator_roles_ids_list=Query(interaction.guild.id)
        if vc_creator_id==0:
            Embed.add_field(name="Auto Vc Creator",value=f"> #channel",inline=False)
        else:
            Embed.add_field(name="Auto Vc Creator",value=f"> {interaction.guild.get_channel(vc_creator_id).mention}",inline=False)
        if moderator_roles_ids_list==0:
            Embed.add_field(name="Moderator Roles",value=f"> @moderator roles",inline=False)
        else:
            Roles=""
            for Role_id in moderator_roles_ids_list:
                Roles+=f"{interaction.guild.get_role(Role_id).mention}, "
            Roles=Roles[:-2]
            Embed.add_field(name="Moderator Roles",value=f"> {Roles}",inline=False)
        if vc_category_id==0:
            Embed.add_field(name="Auto Vc Category",value=f"> #category",inline=False)
        else:
            Embed.add_field(name="Auto Vc Category",value=f"> {interaction.guild.get_channel(vc_category_id).mention}",inline=False)
        if member_role_id==0:
            Embed.add_field(name="Member Role",value=f"> @role",inline=False)
        else:
            Embed.add_field(name="Member Role",value=f"> {interaction.guild.get_role(member_role_id).mention}",inline=False)
        return Embed
    @discord.ui.button(label="Vc Creator",style=discord.ButtonStyle.grey,row=0,custom_id="vc_creator")
    async def vc_creator(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        vc_creator_id,error_message=Vc_Creator_Query(interaction.guild.id)
        if vc_creator_id!=0:
            vc_creator=interaction.guild.get_channel(vc_creator_id).mention
        else:
            vc_creator="#channel"
        view=Vc_Creator_View()
        await interaction.response.send_message(embed=discord.Embed(description=f"The Auto Vc Creator is currently set to {vc_creator}",colour=0x00F3FF),ephemeral=True,view=view)
        await view.wait()
        await interaction.message.edit(embed=self.Embed(interaction),view=Auto_Vcs_Menu_View())
    @discord.ui.button(label="Moderator Roles",style=discord.ButtonStyle.grey,row=0,custom_id="bypass_roles")
    async def bypass_roles(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        moderator_roles_ids_list=Moderator_Roles_Query(interaction.guild.id)
        if moderator_roles_ids_list!=0:
            moderator_roles=""
            for role_id in moderator_roles_ids_list:
                moderator_roles+=f"{interaction.guild.get_role(role_id).mention}, "
            moderator_roles=moderator_roles[:-2]
        else:                
            moderator_roles="@moderator roles"
        view=Bypass_Roles_View()
        await interaction.response.send_message(embed=discord.Embed(description=f"The Moderator Roles are currently set as: {moderator_roles}",colour=0x00F3FF),ephemeral=True,view=view)
        await view.wait()
        await interaction.message.edit(embed=self.Embed(interaction),view=Auto_Vcs_Menu_View())
    @discord.ui.button(label="Vc Category",style=discord.ButtonStyle.grey,row=1,custom_id="vc_category")
    async def vc_Category(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        vc_category_id,error_message=Vc_Category_Query(interaction.guild.id)
        if vc_category_id!=0:
            vc_category=interaction.guild.get_channel(vc_category_id).mention
        else:
            vc_category="#category"
        view=Vc_Category_View()
        await interaction.response.send_message(embed=discord.Embed(description=f"The Auto Vc Category is currently set to {vc_category}",colour=0x00F3FF),ephemeral=True,view=view)
        await view.wait()
        await interaction.message.edit(embed=self.Embed(interaction),view=Auto_Vcs_Menu_View())
    @discord.ui.button(label="Member Role",style=discord.ButtonStyle.grey,row=1,custom_id="member_role")
    async def member_role(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        member_role_id,error_message=Member_Role_Query(interaction.guild.id)
        if member_role_id!=0:
            member_role=interaction.guild.get_role(member_role_id).mention
        else:
            member_role="#role"
        view=Member_Role_View()
        await interaction.response.send_message(embed=discord.Embed(description=f"The Member Role is currently set to {member_role}",colour=0x00F3FF),ephemeral=True,view=view)
        await view.wait()
        await interaction.message.edit(embed=self.Embed(interaction),view=Auto_Vcs_Menu_View())
    @discord.ui.button(emoji="ℹ️",style=discord.ButtonStyle.blurple,row=0,custom_id="auto_vc_information")
    async def information(self,interaction:discord.Interaction,button:discord.ui.Button):
        Embed=discord.Embed(title="Auto Voice Channel Settings Information ℹ️",colour=0x00F3FF)
        Embed.add_field(name="Auto Vc Creator",value="> The permanent channel that will be used to create a new temporary voice channel",inline=False)
        Embed.add_field(name="Moderator Roles",value="> The roles which will always be able to access any created voice channels, regardless if it is hidden/locked",inline=False)
        Embed.add_field(name="Auto Vc Category",value="> The category in which the created voice channels will be located in",inline=False)
        Embed.add_field(name="Member Role",value="> This should be the role that by default can access created voice channels",inline=False)
        await interaction.response.send_message(embed=Embed,ephemeral=True)
    @discord.ui.button(emoji="🗑️",style=discord.ButtonStyle.red,row=1,custom_id="auto_vc_delete")
    async def delete(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        await interaction.response.defer()
        await interaction.message.delete()

class Vc_Creator_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Vc_Creator_Select(self))
class Vc_Creator_Select(discord.ui.ChannelSelect):
    def __init__(self,view_self):
        super().__init__(placeholder="Vc Creator",min_values=1,max_values=1,channel_types=[discord.ChannelType.voice],custom_id="vc_creator_select")
        self.view_self=view_self
    async def callback(self,interaction):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        vc_creator=self.values[0]
        vc_creator_id=vc_creator
        Configure(interaction.guild_id,vc_creator_id=vc_creator_id)
        await interaction.response.edit_message(embed=discord.Embed(description=f"Successfully set the auto vc creator channel to {self.values[0].mention}",colour=0x00F3FF),view=None)
        self.view_self.stop()

class Vc_Category_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Vc_Category_Select(self))
class Vc_Category_Select(discord.ui.ChannelSelect):
    def __init__(self,view_self):
        super().__init__(placeholder="Auto Vc Category",min_values=1,max_values=1,channel_types=[discord.ChannelType.category],custom_id="vc_category_select")
        self.view_self=view_self
    async def callback(self,interaction):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        vc_category=interaction.guild.get_channel(self.values[0].id)
        vc_category_id=vc_category.id
        Configure(interaction.guild_id,vc_category_id=vc_category_id)
        await interaction.response.edit_message(embed=discord.Embed(description=f"Successfully set the auto vc category to {vc_category.mention}",colour=0x00F3FF),view=None)
        self.view_self.stop()

class Member_Role_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Member_Role_Select(self))
class Member_Role_Select(discord.ui.RoleSelect):
    def __init__(self,view_self):
        super().__init__(placeholder="Member Role",min_values=1,max_values=1,custom_id="member_role_select")
        self.view_self=view_self
    async def callback(self,interaction):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        member_role_id=self.values[0].id
        Configure(interaction.guild_id,member_role_id=member_role_id)
        await interaction.response.edit_message(embed=discord.Embed(description=f"Successfully set the member role to {self.values[0].mention}",colour=0x00F3FF),view=None)
        self.view_self.stop()

class Bypass_Roles_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Bypass_Roles_Select(self))
class Bypass_Roles_Select(discord.ui.RoleSelect):
    def __init__(self,view_self):
        super().__init__(placeholder="Moderator Roles",min_values=1,max_values=25,custom_id="bypass_roles_select")
        self.view_self=view_self
    async def callback(self,interaction):
        allowed,error_message=Checks.Admin_Only_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        moderator_roles_ids_list=[]
        Roles=""
        for Role in self.values:
            moderator_roles_ids_list.append(Role.id)
            Roles+=f"{Role.mention}, "
        Roles=Roles[:-2]
        Configure(interaction.guild_id,moderator_roles_ids_list=moderator_roles_ids_list)
        await interaction.response.edit_message(embed=discord.Embed(description=f"Successfully set the moderator roles: {Roles}",colour=0x00F3FF),view=None)
        self.view_self.stop()