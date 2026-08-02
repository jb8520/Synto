from ..models import WelcomeMessageSettings

from .base import execute, fetch_one, ensure_guild_exists


def ensure_welcome_message_settings_exist(guild_id: int) -> None:
    ensure_guild_exists(guild_id)

    query = 'INSERT IGNORE INTO welcome_message_settings (guild_id) VALUES (%s)'

    values = (
        guild_id,
    )

    execute(
        query = query,
        values = values
    )


def get_welcome_message_settings(guild_id: int) -> WelcomeMessageSettings:
    ensure_welcome_message_settings_exist(guild_id)

    query = '''
        SELECT
            guild_id,
            channel_id,
            title,
            description,
            colour,
            status
        FROM welcome_message_settings
        WHERE guild_id = %s
    '''

    values = (
        guild_id,
    )

    row = fetch_one(
        query = query,
        values = values
    )
       
    if row is None:
        return WelcomeMessageSettings(guild_id = guild_id)

    return WelcomeMessageSettings(
        guild_id = int(row['guild_id']),
        channel_id = int(row['channel_id']),
        title = str(row['title']),
        description = row['description'],
        colour = row['colour'],
        status = bool(row['status']),
    )


def get_welcome_channel_id(guild_id: int) -> int:
    return get_welcome_message_settings(guild_id).channel_id

def get_welcome_message_status(guild_id: int) -> bool:
    return get_welcome_message_settings(guild_id).status


def set_welcome_channel(guild_id: int, channel_id: int) -> None:
    ensure_welcome_message_settings_exist(guild_id)

    query = '''
        UPDATE welcome_message_settings
        SET channel_id = %s
        WHERE guild_id = %s
    '''

    values = (
        channel_id,
        guild_id
    )

    execute(
        query = query,
        values = values
    )

def set_welcome_title(guild_id: int, title: str) -> None:
    ensure_welcome_message_settings_exist(guild_id)

    query = '''
        UPDATE welcome_message_settings
        SET title = %s
        WHERE guild_id = %s
    '''

    values =(
        title,
        guild_id
    )
    execute(
        query = query,
        values = values
    )

def set_welcome_description(guild_id: int, description: str | None) -> None:
    ensure_welcome_message_settings_exist(guild_id)

    query = '''
        UPDATE welcome_message_settings
        SET description = %s
        WHERE guild_id = %s
    '''

    values = (
        description,
        guild_id
    )

    execute(
        query = query,
        values = values
    )

def set_welcome_colour(guild_id: int, colour: str | None) -> None:
    ensure_welcome_message_settings_exist(guild_id)

    if colour is not None:
        colour = colour.strip()

        if colour.startswith('#'):
            colour = colour[1:]

    query = '''
        UPDATE welcome_message_settings
        SET colour = %s
        WHERE guild_id = %s
    '''

    values = (
        colour,
        guild_id
    )

    execute(
        query = query,
        values = values
    )

def set_welcome_status(guild_id: int, status: bool) -> None:
    ensure_welcome_message_settings_exist(guild_id)

    query = '''
        UPDATE welcome_message_settings
        SET status = %s
        WHERE guild_id = %s
    '''

    values = (
        status,
        guild_id
    )

    execute(
        query = query,
        values = values
    )


def update_welcome_message_settings(
    guild_id: int,
    channel_id: int | None = None,
    title: str | None = None,
    description: str | None = None,
    colour: str | None = None,
    status: bool | None = None,
) -> None:
    ensure_welcome_message_settings_exist(guild_id)

    if channel_id is not None:
        set_welcome_channel(
            guild_id = guild_id,
            channel_id = channel_id,
        )

    if title is not None:
        set_welcome_title(
            guild_id = guild_id,
            title = title,
        )

    if description is not None:
        set_welcome_description(
            guild_id = guild_id,
            description = description,
        )

    if colour is not None:
        set_welcome_colour(
            guild_id = guild_id,
            colour = colour,
        )

    if status is not None:
        set_welcome_status(
            guild_id = guild_id,
            status = status,
        )


def clear_welcome_description(guild_id: int) -> None:
    set_welcome_description(
        guild_id = guild_id,
        description = None,
    )

def clear_welcome_colour(guild_id: int) -> None:
    set_welcome_colour(
        guild_id = guild_id,
        colour = None,
    )


def reset_welcome_message_settings(guild_id: int) -> None:
    ensure_welcome_message_settings_exist(guild_id)

    query = '''
        UPDATE welcome_message_settings
        SET
            channel_id = 0,
            title = \'Welcome!\',
            description = NULL,
            colour = NULL,
            status = FALSE
        WHERE guild_id = %s
    '''

    values = (
        guild_id,
    )

    execute(
        query = query,
        values = values
    )

def delete_welcome_message_settings(guild_id: int) -> None:
    query = '''
        DELETE FROM welcome_message_settings
        WHERE guild_id = %s
    '''

    values = (
        guild_id,
    )

    execute(
        query = query,
        values = values
    )