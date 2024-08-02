import discord, os
from discord.ext import commands

from DataBase.Auto_Vc import Query

class User_Limit_Modal(discord.ui.Modal,title="User Limit"):
    Selected_Limit=discord.ui.TextInput(label="Enter the User Limit",style=discord.TextStyle.short,placeholder="Enter 0 for no user limit",required=True)
    async def on_submit(self,interaction:discord.Interaction):
        Position=interaction.client.Auto_Vc_Owners[interaction.guild.id].index(interaction.user.id)
        Channel=interaction.guild.get_channel(interaction.client.Auto_Vcs[interaction.guild.id][Position])
        try:
            User_Limit=int(str(self.Selected_Limit))
        except:
            await interaction.response.send_message("❌ The user limit must be a number between 0 and 99",ephemeral=True)
            return
        if 0<=User_Limit<100:
            await Channel.edit(user_limit=int(f"{User_Limit}"))
            await interaction.response.send_message("✅ Success!",ephemeral=True)
        else:
            await interaction.response.send_message("❌ The user limit must be a number between 0 and 99",ephemeral=True)
class Rename_Modal(discord.ui.Modal,title="Rename"):
    Rename=discord.ui.TextInput(label="Rename",style=discord.TextStyle.short,placeholder="Enter the name for the voice channel",required=True)
    async def on_submit(self,interaction:discord.Interaction):
        Position=interaction.client.Auto_Vc_Owners[interaction.guild.id].index(interaction.user.id)
        Channel=interaction.guild.get_channel(interaction.client.Auto_Vcs[interaction.guild.id][Position])
        New_Name=str(self.Rename)
        if 0<len(New_Name)<101:
            await Channel.edit(name=f"{New_Name}")
            await interaction.response.send_message("✅ Success!",ephemeral=True)
        else:
            await interaction.response.send_message("❌ The name must be between 1 and 100 characters",ephemeral=True)
class Permit_View(discord.ui.View):
    def __init__(self,Channel):
        super().__init__()
        self.add_item(Permit_Select(self,Channel))
class Permit_Select(discord.ui.MentionableSelect):
    def __init__(self,View_Self,Channel):
        super().__init__(placeholder="Permit Roles/Members",min_values=1,max_values=25)
        self.View_Self=View_Self
        self.Channel=Channel
    async def callback(self,interaction):
        overwrites=self.Channel.overwrites
        for Option in self.values:
            Object=interaction.guild.get_role(Option.id)
            if Object is None:
                Object=interaction.guild.get_member(Option.id)
            overwrites[Object]=discord.PermissionOverwrite(view_channel=True,connect=True)
        await self.Channel.edit(overwrites=overwrites)
        await interaction.response.send_message("✅ Success!",ephemeral=True)
        self.View_Self.stop()
class Auto_Vc_Buttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(emoji="<:Lock:1167457451134701649>",style=discord.ButtonStyle.grey,custom_id="lock",row=0)
    async def lock(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.id in interaction.client.Auto_Vc_Owners[interaction.guild.id]:
            Position=interaction.client.Auto_Vc_Owners[interaction.guild.id].index(interaction.user.id)
            Channel=interaction.guild.get_channel(interaction.client.Auto_Vcs[interaction.guild.id][Position])
            Member_Role=interaction.guild.get_role(Query(interaction.guild.id,'member_role'))
            Permissions=Channel.overwrites_for(Member_Role)
            Permissions.connect=False
            await Channel.set_permissions(Member_Role,overwrite=Permissions)
            await interaction.response.send_message("✅ Success!",ephemeral=True)
        else:
            await interaction.response.send_message("❌ You need to be the owner of a voice channel to use this button",ephemeral=True)
    @discord.ui.button(emoji="<:Unlock:1177249846105755718>",style=discord.ButtonStyle.grey,custom_id="unlock",row=0)
    async def unlock(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.id in interaction.client.Auto_Vc_Owners[interaction.guild.id]:
            Position=interaction.client.Auto_Vc_Owners[interaction.guild.id].index(interaction.user.id)
            Channel=interaction.guild.get_channel(interaction.client.Auto_Vcs[interaction.guild.id][Position])
            Member_Role=interaction.guild.get_role(Query(interaction.guild.id,'member_role'))
            Permissions=Channel.overwrites_for(Member_Role)
            Permissions.connect=True
            await Channel.set_permissions(Member_Role,overwrite=Permissions)
            await interaction.response.send_message("✅ Success!",ephemeral=True)
        else:
            await interaction.response.send_message("❌ You need to be the owner of a voice channel to use this button",ephemeral=True)
    @discord.ui.button(emoji="<:Hide:1167457445082308638>",style=discord.ButtonStyle.grey,custom_id="hide",row=0)
    async def hide(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.id in interaction.client.Auto_Vc_Owners[interaction.guild.id]:
            Position=interaction.client.Auto_Vc_Owners[interaction.guild.id].index(interaction.user.id)
            Channel=interaction.guild.get_channel(interaction.client.Auto_Vcs[interaction.guild.id][Position])
            Member_Role=interaction.guild.get_role(Query(interaction.guild.id,'member_role'))
            Permissions=Channel.overwrites_for(Member_Role)
            Permissions.view_channel=False
            await Channel.set_permissions(Member_Role,overwrite=Permissions)
            await interaction.response.send_message("✅ Success!",ephemeral=True)
        else:
            await interaction.response.send_message("❌ You need to be the owner of a voice channel to use this button",ephemeral=True)
    @discord.ui.button(emoji="<:Show:1167457420004577370>",style=discord.ButtonStyle.grey,custom_id="show",row=0)
    async def show(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.id in interaction.client.Auto_Vc_Owners[interaction.guild.id]:
            Position=interaction.client.Auto_Vc_Owners[interaction.guild.id].index(interaction.user.id)
            Channel=interaction.guild.get_channel(interaction.client.Auto_Vcs[interaction.guild.id][Position])
            Member_Role=interaction.guild.get_role(Query(interaction.guild.id,'member_role'))
            Permissions=Channel.overwrites_for(Member_Role)
            Permissions.view_channel=True
            await Channel.set_permissions(Member_Role,overwrite=Permissions)
            await interaction.response.send_message("✅ Success!",ephemeral=True)
        else:
            await interaction.response.send_message("❌ You need to be the owner of a voice channel to use this button",ephemeral=True)
    @discord.ui.button(emoji="<:Users:1167457429324304556>",style=discord.ButtonStyle.grey,custom_id="limit",row=1)
    async def user_limit(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.id in interaction.client.Auto_Vc_Owners[interaction.guild.id]:
            await interaction.response.send_modal(User_Limit_Modal())
        else:
            await interaction.response.send_message("❌ You need to be the owner of a voice channel to use this button",ephemeral=True)
    @discord.ui.button(emoji="<:Rename:1167457460852891748>",style=discord.ButtonStyle.grey,custom_id="rename",row=1)
    async def rename(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.id in interaction.client.Auto_Vc_Owners[interaction.guild.id]:
            await interaction.response.send_modal(Rename_Modal())
        else:
            await interaction.response.send_message("❌ You need to be the owner of a voice channel to use this button",ephemeral=True)
    @discord.ui.button(emoji="<:Permit:1167457438576934912>",style=discord.ButtonStyle.grey,custom_id="permit",row=1)
    async def permit(self,interaction:discord.Interaction,button:discord.ui.Button):
        for Channel_Id in interaction.client.Auto_Vcs[interaction.guild.id]:
            Channel=interaction.guild.get_channel(Channel_Id)
            if interaction.user in Channel.members:
                View=Permit_View(Channel)
                await interaction.response.send_message("please choose roles/members to permit to vc",view=View,ephemeral=True)
                await View.wait()
                return
        await interaction.response.send_message("you are not in a valid vc")
    @discord.ui.button(emoji="<:Claim:1174656588338954311>",style=discord.ButtonStyle.grey,custom_id="claim",row=1)
    async def claim_ownership(self,interaction:discord.Interaction,button:discord.ui.Button):
        for Channel_Id in interaction.client.Auto_Vcs[interaction.guild.id]:
            Channel=interaction.guild.get_channel(Channel_Id)
            if interaction.user in Channel.members:
                Position=interaction.client.Auto_Vcs[interaction.guild.id].index(Channel_Id)
                if interaction.client.Auto_Vc_Owners[interaction.guild.id][Position]==interaction.user.id:
                    await interaction.response.send_message("❌ You are already the owner of this voice channel",ephemeral=True)
                    return
                elif interaction.client.Auto_Vc_Owners[interaction.guild.id][Position]==0:
                    interaction.client.Auto_Vc_Owners[interaction.guild.id][Position]=interaction.user.id
                    await interaction.response.send_message("✅ Success!",ephemeral=True)
                    return
                else:
                    for Role_id in Query(interaction.guild.id,'bypass_roles'):
                        Role=interaction.guild.get_role(Role_id)
                        if Role in interaction.user.roles:
                            interaction.client.Auto_Vc_Owners[interaction.guild.id][Position]=interaction.user.id
                            await interaction.response.send_message("✅ Success!",ephemeral=True)
                            return
        await interaction.response.send_message("❌ You are not in a claimable vc",ephemeral=True)
class Auto_Vc(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot=bot
        self.Auto_Vcs=bot.Auto_Vcs
        self.Auto_Vc_Owners=bot.Auto_Vc_Owners
        self.Auto_Vc_Number_Names=bot.Auto_Vc_Number_Names
    @commands.Cog.listener('on_voice_state_update')
    async def voice_update(self,member:discord.Member,before,after):
        Vc_Creator_id=Query(member.guild.id,'vc_creator_id')
        if Vc_Creator_id==0:
            return
        Vc_Creator=self.bot.get_channel(Vc_Creator_id)
        if before.channel!=after.channel and after.channel==Vc_Creator:
            overwrites={
                member.guild.default_role:discord.PermissionOverwrite(view_channel=False,connect=False),
                member.guild.get_role(Query(member.guild.id,'member_role')):discord.PermissionOverwrite(view_channel=True,connect=True),
                member.guild.get_member(int(os.environ["BOT_ID"])):discord.PermissionOverwrite(view_channel=True,manage_channels=True,manage_permissions=True,manage_roles=True)}
            List=Query(member.guild.id,'bypass_roles')
            if List!=0:
                for id in List:
                    Role=member.guild.get_role(id)
                    overwrites[Role]=discord.PermissionOverwrite(view_channel=True,connect=True)
            if member.guild.id not in self.Auto_Vcs:
                Number=1
            else:
                Number=0
                Highest_Name_Number=max(self.Auto_Vcs[member.guild.id])
                for i in range(Highest_Name_Number):
                    if i+1 not in self.Auto_Vc_Number_Names[member.guild.id]:
                        Number=i+1
                        break
                if Number==0:
                    Number=len(self.Auto_Vcs[member.guild.id])+1
            Channel=await member.guild.create_voice_channel(f"VC {Number}",category=self.bot.get_channel(Query(member.guild.id,'vc_category_id')),overwrites=overwrites)
            await member.move_to(Channel)
            if member.guild.id in self.Auto_Vcs:
                self.Auto_Vcs[member.guild.id].append(Channel.id)
                self.Auto_Vc_Owners[member.guild.id].append(member.id)
                self.Auto_Vc_Number_Names[member.guild.id].append(Number)
            else:
                self.Auto_Vcs[member.guild.id]=[Channel.id]
                self.Auto_Vc_Owners[member.guild.id]=[member.id]
                self.Auto_Vc_Number_Names[member.guild.id]=[Number]
        if member.guild.id in self.Auto_Vcs:
            for Channel_Id in self.Auto_Vcs[member.guild.id]:
                Channel=member.guild.get_channel(Channel_Id)
                if before.channel!=after.channel and before.channel==Channel and before.channel.members==[]:
                    Position=self.Auto_Vcs[member.guild.id].index(Channel_Id)
                    self.Auto_Vcs[member.guild.id].pop(Position)
                    self.Auto_Vc_Owners[member.guild.id].pop(Position)
                    self.Auto_Vc_Number_Names[member.guild.id].pop(Position)
                    if self.Auto_Vcs[member.guild.id]==[]:
                        del self.Auto_Vcs[member.guild.id]
                        del self.Auto_Vc_Owners[member.guild.id]
                        del self.Auto_Vc_Number_Names[member.guild.id]
                    await Channel.delete()
                    return
                elif before.channel!=after.channel and before.channel==Channel and member.id in self.Auto_Vc_Owners[member.guild.id]:
                    Position=self.Auto_Vc_Owners[member.guild.id].index(member.id)
                    self.Auto_Vc_Owners[member.guild.id][Position]=0
                    return
async def setup(bot:commands.Bot):
    await bot.add_cog(Auto_Vc(bot))