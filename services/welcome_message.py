import datetime

import discord

from discord import Member
from discord.ext import commands

from database.repositories import (
    get_welcome_message_settings,
    log_welcome_message
)


DEFAULT_WELCOME_COLOUR = discord.Colour.from_str('#000000')


def format_welcome_text(
    text: str | None,
    member: discord.Member
) -> str | None:
    if text is None:
        return None

    if text.lower() == 'none':
        return None

    return (
        text
        .replace('{member}', member.mention)
        .replace('{member_name}', member.display_name)
        .replace('{server}', member.guild.name)
    )


def parse_embed_colour(colour: str | None) -> discord.Colour:
    if colour is None:
        return DEFAULT_WELCOME_COLOUR

    colour = colour.strip()

    if colour.lower() == 'none':
        return DEFAULT_WELCOME_COLOUR

    if not colour.startswith('#'):
        colour = f'#{colour}'

    try:
        return discord.Colour.from_str(colour)

    except ValueError:
        return DEFAULT_WELCOME_COLOUR
    

async def send_welcome_message(bot: commands.Bot, member: Member):
    settings = get_welcome_message_settings(member.guild.id)

    if not settings.status:
        return

    welcome_channel = bot.get_channel(settings.channel_id)

    if not isinstance(welcome_channel, discord.TextChannel):
        return

    title = format_welcome_text(
        text = settings.title,
        member = member
    )
    
    description = format_welcome_text(
        text = settings.description,
        member = member
    )

    colour = parse_embed_colour(settings.colour)

    embed = discord.Embed(
        title = title,
        description = description,
        colour = colour,
        timestamp = datetime.datetime.now(datetime.UTC)
    )

    embed.set_thumbnail(url = member.display_avatar.url)

    embed.add_field(
        name = 'Account Created',
        value = f'<t:{round(member.created_at.timestamp())}:R>',
        inline = False
    )

    embed.add_field(
        name = 'ID',
        value = str(member.id),
        inline = False
    )

    embed.set_footer(text = f'Powered by Synto')

    await welcome_channel.send(embed = embed)

    log_welcome_message(
        user_id = member.id,
        guild_id = member.guild.id
    )