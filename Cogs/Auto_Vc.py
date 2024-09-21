import discord
from discord.ext import commands

import Checks

from DataBase.Auto_Vc import Query, Member_Role_Query, Moderator_Roles_Query

class User_Limit_Modal(discord.ui.Modal,title='User Limit'):
    selected_limit=discord.ui.TextInput(label='Enter the User Limit',style=discord.TextStyle.short,placeholder='Enter 0 for no user limit',required=True)
    async def on_submit(self,interaction:discord.Interaction):
        position=interaction.client.auto_vc_owners[interaction.guild.id].index(interaction.user.id)
        channel=interaction.guild.get_channel(interaction.client.auto_vcs[interaction.guild.id][position])
        try:
            user_limit=int(str(self.selected_limit))
        except:
            await interaction.response.send_message('❌ The user limit must be a number between 0 and 99',ephemeral=True)
            return
        if 0<=user_limit<100:
            await channel.edit(user_limit=int(f'{user_limit}'))
            await interaction.response.send_message('✅ Success!',ephemeral=True)
        else:
            await interaction.response.send_message('❌ The user limit must be a number between 0 and 99',ephemeral=True)

class Rename_Modal(discord.ui.Modal,title='Rename'):
    rename=discord.ui.TextInput(label='Rename',style=discord.TextStyle.short,placeholder='Enter the name for the voice channel',required=True)
    async def on_submit(self,interaction:discord.Interaction):
        position=interaction.client.auto_vc_owners[interaction.guild.id].index(interaction.user.id)
        channel=interaction.guild.get_channel(interaction.client.auto_vcs[interaction.guild.id][position])
        new_name=str(self.rename)
        if 0<len(new_name)<101:
            await channel.edit(name=f'{new_name}')
            await interaction.response.send_message('✅ Success!',ephemeral=True)
        else:
            await interaction.response.send_message('❌ The name must be between 1 and 100 characters',ephemeral=True)

class Invite_View(discord.ui.View):
    def __init__(self,channel):
        super().__init__()
        self.add_item(Invite_Select(self,channel))

class Invite_Select(discord.ui.MentionableSelect):
    def __init__(self,View_Self:discord.ui.View,channel:discord.VoiceChannel):
        super().__init__(placeholder='Permit Roles/Members',min_values=1,max_values=25)
        self.View_Self=View_Self
        self.channel=channel
    
    async def callback(self,interaction):
        overwrites=self.channel.overwrites
        for option in self.values:
            object=interaction.guild.get_role(option.id)
            if object is None:
                object=interaction.guild.get_member(option.id)
            overwrites[object]=discord.PermissionOverwrite(view_channel=True,connect=True)
        await self.channel.edit(overwrites=overwrites)
        await interaction.response.send_message('✅ Success!',ephemeral=True)
        self.View_Self.stop()

class Auto_Vc_Buttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(emoji='<:Lock:1167457451134701649>',style=discord.ButtonStyle.grey,custom_id='lock',row=0)
    async def lock(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Auto_Vc_Owner_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        try:
            auto_vcs:list=interaction.client.auto_vcs[interaction.guild.id]
            auto_vc_owners:list=interaction.client.auto_vc_owners[interaction.guild.id]
        except KeyError:
            auto_vcs=[]
            auto_vc_owners=[]
        position=auto_vc_owners.index(interaction.user.id)
        channel=interaction.guild.get_channel(auto_vcs[position])
        member_role_id,error_message=Member_Role_Query(interaction.guild.id)
        try:
            member_role=interaction.guild.get_role(member_role_id)
        except AttributeError:
            await interaction.response.send_message('❌ An error occured! Please try again and if the issue persists contact synto support',ephemeral=True)
        permissions=channel.overwrites_for(member_role)
        permissions.connect=False
        await channel.set_permissions(member_role,overwrite=permissions)
        await interaction.response.send_message('✅ Success!',ephemeral=True)
    
    @discord.ui.button(emoji='<:Unlock:1177249846105755718>',style=discord.ButtonStyle.grey,custom_id='unlock',row=0)
    async def unlock(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Auto_Vc_Owner_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        try:
            auto_vcs:list=interaction.client.auto_vcs[interaction.guild.id]
            auto_vc_owners:list=interaction.client.auto_vc_owners[interaction.guild.id]
        except KeyError:
            auto_vcs=[]
            auto_vc_owners=[]
        position=auto_vc_owners.index(interaction.user.id)
        channel=interaction.guild.get_channel(auto_vcs[position])
        member_role_id,error_message=Member_Role_Query(interaction.guild.id)
        try:
            member_role=interaction.guild.get_role(member_role_id)
        except AttributeError:
            await interaction.response.send_message('❌ An error occured! Please try again and if the issue persists contact synto support',ephemeral=True)
        permissions=channel.overwrites_for(member_role)
        permissions.connect=True
        await channel.set_permissions(member_role,overwrite=permissions)
        await interaction.response.send_message('✅ Success!',ephemeral=True)
    
    @discord.ui.button(emoji='<:Hide:1167457445082308638>',style=discord.ButtonStyle.grey,custom_id='hide',row=0)
    async def hide(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Auto_Vc_Owner_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        try:
            auto_vcs:list=interaction.client.auto_vcs[interaction.guild.id]
            auto_vc_owners:list=interaction.client.auto_vc_owners[interaction.guild.id]
        except KeyError:
            auto_vcs=[]
            auto_vc_owners=[]
        position=auto_vc_owners.index(interaction.user.id)
        channel=interaction.guild.get_channel(auto_vcs[position])
        member_role_id,error_message=Member_Role_Query(interaction.guild.id)
        try:
            member_role=interaction.guild.get_role(member_role_id)
        except AttributeError:
            await interaction.response.send_message('❌ An error occured! Please try again and if the issue persists contact synto support',ephemeral=True)
        permissions=channel.overwrites_for(member_role)
        permissions.view_channel=False
        await channel.set_permissions(member_role,overwrite=permissions)
        await interaction.response.send_message('✅ Success!',ephemeral=True)
    
    @discord.ui.button(emoji='<:Show:1167457420004577370>',style=discord.ButtonStyle.grey,custom_id='show',row=0)
    async def show(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Auto_Vc_Owner_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        try:
            auto_vcs:list=interaction.client.auto_vcs[interaction.guild.id]
            auto_vc_owners:list=interaction.client.auto_vc_owners[interaction.guild.id]
        except KeyError:
            auto_vcs=[]
            auto_vc_owners=[]
        position=auto_vc_owners.index(interaction.user.id)
        channel=interaction.guild.get_channel(auto_vcs[position])
        member_role_id,error_message=Member_Role_Query(interaction.guild.id)
        try:
            member_role=interaction.guild.get_role(member_role_id)
        except AttributeError:
            await interaction.response.send_message('❌ An error occured! Please try again and if the issue persists contact synto support',ephemeral=True)
        permissions=channel.overwrites_for(member_role)
        permissions.view_channel=True
        await channel.set_permissions(member_role,overwrite=permissions)
        await interaction.response.send_message('✅ Success!',ephemeral=True)
    
    @discord.ui.button(emoji='<:Users:1167457429324304556>',style=discord.ButtonStyle.grey,custom_id='limit',row=1)
    async def user_limit(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Auto_Vc_Owner_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        await interaction.response.send_modal(User_Limit_Modal())
    
    @discord.ui.button(emoji='<:Rename:1167457460852891748>',style=discord.ButtonStyle.grey,custom_id='rename',row=1)
    async def rename(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Auto_Vc_Owner_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        await interaction.response.send_modal(Rename_Modal())
    
    @discord.ui.button(emoji='<:Invite:1167457438576934912>',style=discord.ButtonStyle.grey,custom_id='invite',row=1)
    async def invite(self,interaction:discord.Interaction,button:discord.ui.Button):
        allowed,error_message=Checks.Auto_Vc_Owner_Interaction(interaction)
        if not(allowed):
            await interaction.response.send_message(error_message,ephemeral=True)
            return
        try:
            auto_vcs:list=interaction.client.auto_vcs[interaction.guild.id]
            auto_vc_owners:list=interaction.client.auto_vc_owners[interaction.guild.id]
        except KeyError:
            auto_vcs=[]
            auto_vc_owners=[]
        position=auto_vc_owners.index(interaction.guild.id)
        channel_id=auto_vcs[position]
        channel=interaction.guild.get_channel(channel_id)
        view=Invite_View(channel)
        await interaction.response.send_message('Please select the roles and/or members you want to give access to this voice channel',view=view,ephemeral=True)
        await view.wait()
    
    @discord.ui.button(emoji='<:Claim:1174656588338954311>',style=discord.ButtonStyle.grey,custom_id='claim',row=1)
    async def claim_ownership(self,interaction:discord.Interaction,button:discord.ui.Button):
        try:
            auto_vcs:list=interaction.client.auto_vcs[interaction.guild.id]
            auto_vc_owners:list=interaction.client.auto_vc_owners[interaction.guild.id]
        except KeyError:
            auto_vcs=[]
            auto_vc_owners=[]
        for channel_id in auto_vcs:
            channel=interaction.guild.get_channel(channel_id)
            if interaction.user in channel.members:
                position=auto_vcs.index(channel_id)
                if auto_vc_owners[position]==interaction.user.id:
                    await interaction.response.send_message('❌ You are already the owner of this voice channel',ephemeral=True)
                    return
                elif auto_vc_owners[position]==0:
                    auto_vc_owners[position]=interaction.user.id
                    await interaction.response.send_message('✅ Success!',ephemeral=True)
                    return
                else:
                    moderator_roles_ids_list=Moderator_Roles_Query(interaction.guild.id)
                    if moderator_roles_ids_list!=[0]:
                        for id in moderator_roles_ids_list:
                            role=interaction.guild.get_role(id)
                            if role in interaction.user.roles:
                                auto_vc_owners[position]=interaction.user.id
                                await interaction.response.send_message('✅ Success!',ephemeral=True)
                                return
        await interaction.response.send_message('❌ You are not in a claimable vc',ephemeral=True)

class Auto_Vc(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot=bot
        self.auto_vcs:dict=bot.auto_vcs
        self.auto_vc_owners:dict=bot.auto_vc_owners
        self.auto_vc_number_names=bot.auto_vc_number_names
    
    @commands.Cog.listener('on_voice_state_update')
    async def voice_update(self,member:discord.Member,before:discord.VoiceState,after:discord.VoiceState):
        vc_creator_id,vc_category_id,member_role_id,moderator_roles_ids_list=Query(member.guild.id)
        if vc_creator_id==0:
            return
        vc_creator=self.bot.get_channel(vc_creator_id)
        if before.channel!=after.channel and after.channel==vc_creator:
            overwrites={
                member.guild.default_role:discord.PermissionOverwrite(view_channel=False,connect=False),
                member.guild.get_role(member_role_id):discord.PermissionOverwrite(view_channel=True,connect=True)}
            if moderator_roles_ids_list!=[0]:
                for id in moderator_roles_ids_list:
                    role=member.guild.get_role(id)
                    overwrites[role]=discord.PermissionOverwrite(view_channel=True,connect=True)
            if member.guild.id not in self.auto_vcs:
                number=1
            else:
                number=0
                highest_current_number=max(self.auto_vc_number_names[member.guild.id])
                for i in range(highest_current_number):
                    if i+1 not in self.auto_vc_number_names[member.guild.id]:
                        number=i+1
                        break
                if number==0:
                    number=len(self.auto_vcs[member.guild.id])+1
            channel=await member.guild.create_voice_channel(f"VC {number}",category=self.bot.get_channel(vc_category_id),overwrites=overwrites)
            await member.move_to(channel)
            if member.guild.id in self.auto_vcs:
                self.auto_vcs[member.guild.id].append(channel.id)
                self.auto_vc_owners[member.guild.id].append(member.id)
                self.auto_vc_number_names[member.guild.id].append(number)
            else:
                self.auto_vcs[member.guild.id]=[channel.id]
                self.auto_vc_owners[member.guild.id]=[member.id]
                self.auto_vc_number_names[member.guild.id]=[number]
        if member.guild.id in self.auto_vcs:
            for channel_id in self.auto_vcs[member.guild.id]:
                channel=member.guild.get_channel(channel_id)
                if before.channel!=after.channel and before.channel==channel and before.channel.members==[]:
                    position=self.auto_vcs[member.guild.id].index(channel_id)
                    self.auto_vcs[member.guild.id].pop(position)
                    self.auto_vc_owners[member.guild.id].pop(position)
                    self.auto_vc_number_names[member.guild.id].pop(position)
                    if self.auto_vcs[member.guild.id]==[]:
                        del self.auto_vcs[member.guild.id]
                        del self.auto_vc_owners[member.guild.id]
                        del self.auto_vc_number_names[member.guild.id]
                    await channel.delete()
                    return
                elif before.channel!=after.channel and before.channel==channel and member.id in self.auto_vc_owners[member.guild.id]:
                    position=self.auto_vc_owners[member.guild.id].index(member.id)
                    self.auto_vc_owners[member.guild.id][position]=0
                    return
                

async def setup(bot:commands.Bot):
    await bot.add_cog(Auto_Vc(bot))