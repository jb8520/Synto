from ..models import CountingSettings

from .base import fetch_one, execute, execute_get_rowcount, ensure_guild_exists


def ensure_counting_settings_exist(guild_id: int) -> None:
    ensure_guild_exists(guild_id)

    query = 'INSERT IGNORE INTO counting_settings (guild_id) VALUES (%s)'

    values = (
        guild_id,
    )

    execute(
        query = query ,
        values = values
    )


def get_counting_settings(guild_id: int) -> CountingSettings:
    ensure_counting_settings_exist(guild_id)

    query = '''
        SELECT
            guild_id,
            channel_id,
            highscore,
            current_score,
            last_message_id,
            last_author_id,
            double_count,
            counting_saves_enabled
        FROM counting_settings
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
        return CountingSettings(guild_id = guild_id)

    return CountingSettings(
        guild_id = row['guild_id'],
        channel_id = row['channel_id'],
        highscore = row['highscore'],
        current_score = row['current_score'],
        last_message_id = row['last_message_id'],
        last_author_id = row['last_author_id'],
        double_count = bool(row['double_count']),
        counting_saves_enabled = bool(row['counting_saves_enabled']),
    )


def set_counting_channel(guild_id: int, channel_id: int) -> None:
    ensure_counting_settings_exist(guild_id)

    query = '''
        UPDATE counting_settings
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

def set_double_count(guild_id: int, status: bool) -> None:
    ensure_counting_settings_exist(guild_id)

    query = '''
        UPDATE counting_settings
        SET double_count = %s
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

def toggle_double_count(guild_id: int) -> bool:
    settings = get_counting_settings(guild_id)

    new_value = not settings.double_count

    set_double_count(
        guild_id = guild_id,
        status = new_value
    )

    return new_value


def set_counting_saves_enabled(guild_id: int, enabled: bool) -> None:
    ensure_counting_settings_exist(guild_id)

    query = '''
        UPDATE counting_settings
        SET counting_saves_enabled = %s
        WHERE guild_id = %s
    '''

    values = (
        enabled,
        guild_id
    )

    execute(
        query = query,
        values = values
    )

def toggle_counting_saves_enabled(guild_id: int) -> bool:
    settings = get_counting_settings(guild_id)

    new_value = not settings.counting_saves_enabled

    set_counting_saves_enabled(
        guild_id = guild_id,
        enabled = new_value
    )

    return new_value

def update_current_score(
    guild_id: int,
    current_score: int,
    last_message_id: int = 0,
    last_author_id: int = 0,
) -> None:
    ensure_counting_settings_exist(guild_id)

    query = '''
        UPDATE counting_settings
        SET
            current_score = %s,
            last_message_id = %s,
            last_author_id = %s
        WHERE guild_id = %s
    '''

    values = (
        current_score,
        last_message_id,
        last_author_id,
        guild_id
    )

    execute(
        query = query,
        values = values
    )

def advance_count_if_unchanged(
    guild_id: int,
    expected_current_score: int,
    new_score: int,
    last_message_id: int,
    last_author_id: int
) -> bool:
    query = '''
        UPDATE counting_settings
        SET
            current_score = %s,
            last_message_id = %s,
            last_author_id = %s
        WHERE guild_id = %s AND current_score = %s
    '''

    values = (
        new_score,
        last_message_id,
        last_author_id,
        guild_id,
        expected_current_score
    )

    rowcount = execute_get_rowcount(
        query = query,
        values = values
    )

    return rowcount == 1

def reset_current_score(guild_id: int) -> None:
    update_current_score(
        guild_id = guild_id,
        current_score = 0,
        last_message_id = 0,
        last_author_id = 0,
    )

def update_highscore(guild_id: int, highscore: int) -> None:
    ensure_counting_settings_exist(guild_id)

    query = '''
        UPDATE counting_settings
        SET highscore = %s
        WHERE guild_id = %s
    '''

    values = (
        highscore,
        guild_id
    )

    execute(
        query = query,
        values = values
    )

def update_highscore_if_needed(guild_id: int) -> None:
    settings = get_counting_settings(guild_id)

    if settings.current_score > settings.highscore:
        update_highscore(
            guild_id = guild_id,
            highscore = settings.current_score,
        )

def reset_counting_progress(guild_id: int) -> None:
    update_highscore_if_needed(guild_id)
    
    reset_current_score(guild_id)

def delete_counting_settings(guild_id: int) -> None:
    query = '''
        DELETE FROM counting_settings
        WHERE guild_id = %s
    '''

    values = (
        guild_id,
    )

    execute(
        query = query,
        values = values
    )