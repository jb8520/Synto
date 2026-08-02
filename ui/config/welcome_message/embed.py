from discord import (
    Embed,
    Interaction,
    User,
    Member
)

from database.repositories import get_welcome_message_settings

from .. import SETTINGS_COLOUR


def _get_embed_colour(colour: str | None) -> int:
    if colour is None:
        return SETTINGS_COLOUR

    colour = colour.strip()

    if colour.startswith('#'):
        colour = colour[1:]

    try:
        return int(colour, 16)
    except ValueError:
        return SETTINGS_COLOUR
    

def build_welcome_message_embed(interaction: Interaction) -> Embed:
    settings = get_welcome_message_settings(interaction.guild.id)

    if settings.channel_id == 0:
        channel = '`Not set`'
    else:
        discord_channel = interaction.guild.get_channel(settings.channel_id)
        channel = (
            discord_channel.mention
            if discord_channel is not None
            else '`Unknown channel`'
        )

    title = settings.title.strip() or '`Not set`'

    description = (
        settings.description
        if settings.description is not None and settings.description.strip() != ''
        else '`Not set`'
    )

    colour = (
        f'`#{settings.normalised_colour}`'
        if settings.colour is not None
        else '`Not set`'
    )

    status = '`Enabled`' if settings.status else '`Disabled`'

    embed = Embed(
        title = 'Welcome Message Settings',
        description = 'Configure the welcome message sent when members join the server.',
        colour = _get_embed_colour(settings.colour)
    )

    embed.add_field(
        name = 'Welcome Channel',
        value = f'> {channel}',
        inline = False
    )

    embed.add_field(
        name = 'Title',
        value = f'> {title}',
        inline = False
    )

    embed.add_field(
        name = 'Description',
        value = f'> {description}',
        inline = False
    )

    embed.add_field(
        name = 'Colour',
        value = f'> {colour}',
        inline = False
    )

    embed.add_field(
        name = 'Status',
        value = f'> {status}',
        inline = False
    )

    return embed

def build_welcome_preview_embed(
    interaction: Interaction,
    member: Member | User,
    title: str,
    description: str | None,
    colour: str | None
) -> Embed:
    title = title.strip() or 'Welcome!'

    title = title.replace('{member}', f'{member.mention}')
    title = title.replace('{member_name}', f'{member.display_name}')
    title = title.replace('{server}', f'{interaction.guild.name}')

    if description:
        description = description.replace('{member}', f'{member.mention}')
        description = description.replace('{member_name}', f'{member.display_name}')
        description = description.replace('{server}', f'{interaction.guild.name}')

        if description.strip() == '':
            description = None

    colour =_get_embed_colour(colour)

    embed = Embed(
        title = title,
        description = description,
        colour = colour
    )

    embed.set_thumbnail(url = member.display_avatar.url)

    return embed