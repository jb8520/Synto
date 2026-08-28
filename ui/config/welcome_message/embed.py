from discord import (
    Embed,
    Interaction,
    User,
    Member
)

from database.repositories import get_welcome_message_settings

from services.welcome_message import format_welcome_text

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

    stripped_title = settings.title.strip()
    title = (
        f'`{stripped_title}`'
        if stripped_title and stripped_title.lower() != 'none'
        else '`Not set`'
    )

    stripped_description = (settings.description or '').strip()
    description = (
        stripped_description
        if stripped_description and stripped_description.lower() != 'none'
        else '`Not set`'
    )

    colour = (
        f'`#{settings.normalised_colour}`'
        if settings.colour is not None
        else '`Not set`'
    )

    configured = '`Yes`' if settings.is_configured else '`No`'

    embed = Embed(
        title = '👋 Welcome Message Settings',
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
        name = 'Configured',
        value = f'> {configured}',
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
    # Reuse the exact formatting used when actually sending a welcome message,
    # so the preview always matches what a real member join will produce
    # (e.g. a title/description of "none" is omitted in both places).
    title = format_welcome_text(text = title, member = member)
    description = format_welcome_text(text = description, member = member)

    colour = _get_embed_colour(colour)

    embed = Embed(
        title = title,
        description = description,
        colour = colour
    )

    embed.set_thumbnail(url = member.display_avatar.url)

    return embed