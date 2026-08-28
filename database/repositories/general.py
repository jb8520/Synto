from ..models import GeneralSettings

from .base import (
    ensure_guild_exists,
    execute,
    execute_many,
    fetch_one,
    fetch_all
)


def ensure_general_settings_exist(guild_id: int) -> None:
    ensure_guild_exists(guild_id)

    query = 'INSERT IGNORE INTO general_settings (guild_id) VALUES (%s)'

    values = (
        guild_id,
    )

    execute(
        query = query,
        values = values
    )


def get_general_admin_role_ids(guild_id: int) -> list[int]:
    query = '''
        SELECT role_id
        FROM general_admin_roles
        WHERE guild_id = %s
        ORDER BY role_id
    '''

    values = (
        guild_id,
    )

    rows = fetch_all(
        query = query,
        values = values
    )

    return [
        int(row['role_id'])
        for row in rows
    ]


def set_general_admin_roles(guild_id: int, role_ids: list[int]) -> None:
    unique_role_ids = sorted(set(role_ids))

    execute(
        query = 'DELETE FROM general_admin_roles WHERE guild_id = %s',
        values = (guild_id,)
    )

    if not unique_role_ids:
        return

    ensure_guild_exists(guild_id)

    query = '''
        INSERT INTO general_admin_roles (guild_id, role_id)
        VALUES (%s, %s)
    '''

    values = [
        (guild_id, role_id)
        for role_id in unique_role_ids
    ]

    execute_many(
        query = query,
        values = values
    )


def get_general_settings(guild_id: int) -> GeneralSettings:
    ensure_general_settings_exist(guild_id)

    query = '''
        SELECT
            guild_id,
            auto_vc_enabled,
            counting_enabled,
            games_enabled,
            embed_colour,
            updates_channel_id
        FROM general_settings
        WHERE guild_id = %s
    '''

    values = (
        guild_id,
    )

    row = fetch_one(
        query = query,
        values = values
    )

    admin_role_ids = get_general_admin_role_ids(guild_id)

    if row is None:
        return GeneralSettings(guild_id = guild_id, admin_role_ids = admin_role_ids)

    return GeneralSettings(
        guild_id = int(row['guild_id']),
        auto_vc_enabled = bool(row['auto_vc_enabled']),
        counting_enabled = bool(row['counting_enabled']),
        games_enabled = bool(row['games_enabled']),
        embed_colour = row['embed_colour'],
        updates_channel_id = int(row['updates_channel_id']),
        admin_role_ids = admin_role_ids
    )


def set_auto_vc_module_enabled(guild_id: int, enabled: bool) -> None:
    ensure_general_settings_exist(guild_id)

    execute(
        query = 'UPDATE general_settings SET auto_vc_enabled = %s WHERE guild_id = %s',
        values = (enabled, guild_id)
    )

def toggle_auto_vc_module_enabled(guild_id: int) -> bool:
    new_value = not get_general_settings(guild_id).auto_vc_enabled

    set_auto_vc_module_enabled(guild_id, new_value)

    return new_value


def set_counting_module_enabled(guild_id: int, enabled: bool) -> None:
    ensure_general_settings_exist(guild_id)

    execute(
        query = 'UPDATE general_settings SET counting_enabled = %s WHERE guild_id = %s',
        values = (enabled, guild_id)
    )

def toggle_counting_module_enabled(guild_id: int) -> bool:
    new_value = not get_general_settings(guild_id).counting_enabled

    set_counting_module_enabled(guild_id, new_value)

    return new_value


def set_games_module_enabled(guild_id: int, enabled: bool) -> None:
    ensure_general_settings_exist(guild_id)

    execute(
        query = 'UPDATE general_settings SET games_enabled = %s WHERE guild_id = %s',
        values = (enabled, guild_id)
    )

def toggle_games_module_enabled(guild_id: int) -> bool:
    new_value = not get_general_settings(guild_id).games_enabled

    set_games_module_enabled(guild_id, new_value)

    return new_value


def set_general_embed_colour(guild_id: int, colour: str | None) -> None:
    ensure_general_settings_exist(guild_id)

    if colour is not None:
        colour = colour.strip()

        if colour.startswith('#'):
            colour = colour[1:]

    execute(
        query = 'UPDATE general_settings SET embed_colour = %s WHERE guild_id = %s',
        values = (colour, guild_id)
    )


def set_updates_channel(guild_id: int, channel_id: int) -> None:
    ensure_general_settings_exist(guild_id)

    execute(
        query = 'UPDATE general_settings SET updates_channel_id = %s WHERE guild_id = %s',
        values = (channel_id, guild_id)
    )


def get_guilds_with_updates_channel() -> list[tuple[int, int]]:
    query = '''
        SELECT guild_id, updates_channel_id
        FROM general_settings
        WHERE updates_channel_id != 0
    '''

    rows = fetch_all(query = query)

    return [
        (int(row['guild_id']), int(row['updates_channel_id']))
        for row in rows
    ]
