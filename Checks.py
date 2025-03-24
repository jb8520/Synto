import discord
from discord.ext import commands

import os


# ctx functions
def Bot_Owner_Ctx(ctx:commands.Context):
    if ctx.author.id==int(os.environ['BOT_OWNER_ID']):
        Allowed=True
    else:
        Allowed=False
    return Allowed


# interaction functions
def Admin_Only_Interaction(interaction:discord.Interaction):
    if interaction.user.guild_permissions.administrator or interaction.user.id==int(os.environ['BOT_OWNER_ID']):
        Allowed=True
    else:
        Allowed=False
    return Allowed,'❌ You need to have the administrator permission to use this feature'

def Auto_Vc_Owner_Interaction(interaction:discord.Interaction):
    auto_vc_owners:list=interaction.client.auto_vc_owners[interaction.guild.id]
    if interaction.user.id in auto_vc_owners:
        Allowed=True
    else:
        Allowed=False
    return Allowed,'❌ You need to be the owner of a voice channel to use this button'