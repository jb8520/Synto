from ..models import AutoVCSettings

from .base import fetch_all, fetch_one, execute, execute_many, ensure_guild_exists


from ..models import AutoVCSettings

from .base import (
    ensure_guild_exists,
    execute,
    execute_many,
    fetch_all,
    fetch_one
)


DEFAULT_AUTO_VC_NAME = 'VC'
DEFAULT_CHANNEL_NAME_TEMPLATE = '{name} {number}'


def _build_auto_vc_settings(row: dict) -> AutoVCSettings:
    moderator_role_ids = get_auto_vc_moderator_role_ids(
        auto_vc_id = int(row['id'])
    )

    return AutoVCSettings(
        id = int(row['id']),
        guild_id = int(row['guild_id']),
        name = row['name'],
        vc_creator_id = row['vc_creator_id'],
        vc_category_id = row['vc_category_id'],
        member_role_id = row['member_role_id'],
        moderator_role_ids = moderator_role_ids,
        is_enabled = bool(row['is_enabled']),
        is_default = bool(row['is_default']),
        position = int(row['position']),
        channel_name_template = row['channel_name_template']
    )


def _select_auto_vc_settings_fields() -> str:
    return '''
        id,
        guild_id,
        name,
        vc_creator_id,
        vc_category_id,
        member_role_id,
        is_enabled,
        is_default,
        position,
        channel_name_template
    '''


def count_auto_vc_settings(guild_id: int) -> int:
    query = '''
        SELECT COUNT(*) AS count
        FROM auto_vc_settings
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
        return 0

    return int(row['count'])


def ensure_default_auto_vc_settings_exist(guild_id: int) -> None:
    ensure_guild_exists(guild_id)

    existing_default = get_default_auto_vc_settings(
        guild_id = guild_id,
        create_if_missing = False
    )

    if existing_default is not None:
        return

    existing_settings = get_auto_vc_settings_for_guild(
        guild_id = guild_id
    )

    if existing_settings:
        set_default_auto_vc(
            auto_vc_id = existing_settings[0].id
        )
        return

    create_auto_vc_settings(
        guild_id = guild_id,
        name = DEFAULT_AUTO_VC_NAME,
        is_default = True
    )


def create_auto_vc_settings(
    guild_id: int,
    name: str = DEFAULT_AUTO_VC_NAME,
    is_default: bool = False
) -> int:
    ensure_guild_exists(guild_id)

    next_position = get_next_auto_vc_position(
        guild_id = guild_id
    )

    query = '''
        INSERT INTO auto_vc_settings (
            guild_id,
            name,
            is_default,
            position
        )
        VALUES (%s, %s, %s, %s)
    '''

    values = (
        guild_id,
        name,
        is_default,
        next_position
    )

    result = execute(
        query = query,
        values = values
    )

    if hasattr(result, 'lastrowid') and result.lastrowid is not None:
        return int(result.lastrowid)

    row = fetch_one(
        query = '''
            SELECT id
            FROM auto_vc_settings
            WHERE guild_id = %s
            ORDER BY id DESC
            LIMIT 1
        ''',
        values = (
            guild_id,
        )
    )

    if row is None:
        raise RuntimeError('Failed to create Auto VC settings.')

    return int(row['id'])


def get_next_auto_vc_position(guild_id: int) -> int:
    query = '''
        SELECT COALESCE(MAX(position), 0) + 1 AS next_position
        FROM auto_vc_settings
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
        return 1

    return int(row['next_position'])


def get_auto_vc_settings(auto_vc_id: int) -> AutoVCSettings | None:
    query = f'''
        SELECT
            {_select_auto_vc_settings_fields()}
        FROM auto_vc_settings
        WHERE id = %s
        LIMIT 1
    '''

    values = (
        auto_vc_id,
    )

    row = fetch_one(
        query = query,
        values = values
    )

    if row is None:
        return None

    return _build_auto_vc_settings(row)


def get_default_auto_vc_settings(
    guild_id: int,
    create_if_missing: bool = True
) -> AutoVCSettings | None:
    if create_if_missing:
        ensure_guild_exists(guild_id)

    query = f'''
        SELECT
            {_select_auto_vc_settings_fields()}
        FROM auto_vc_settings
        WHERE
            guild_id = %s
            AND is_default = TRUE
        LIMIT 1
    '''

    values = (
        guild_id,
    )

    row = fetch_one(
        query = query,
        values = values
    )

    if row is not None:
        return _build_auto_vc_settings(row)

    if not create_if_missing:
        return None

    auto_vc_id = create_auto_vc_settings(
        guild_id = guild_id,
        name = DEFAULT_AUTO_VC_NAME,
        is_default = True
    )

    return get_auto_vc_settings(
        auto_vc_id = auto_vc_id
    )


def get_auto_vc_settings_for_guild(guild_id: int) -> list[AutoVCSettings]:
    ensure_guild_exists(guild_id)

    query = f'''
        SELECT
            {_select_auto_vc_settings_fields()}
        FROM auto_vc_settings
        WHERE guild_id = %s
        ORDER BY
            is_default DESC,
            position ASC,
            id ASC
    '''

    values = (
        guild_id,
    )

    rows = fetch_all(
        query = query,
        values = values
    )

    return [
        _build_auto_vc_settings(row)
        for row in rows
    ]


def get_auto_vc_settings_by_creator_channel(
    guild_id: int,
    vc_creator_id: int
) -> AutoVCSettings | None:
    query = f'''
        SELECT
            {_select_auto_vc_settings_fields()}
        FROM auto_vc_settings
        WHERE
            guild_id = %s
            AND vc_creator_id = %s
            AND is_enabled = TRUE
        LIMIT 1
    '''

    values = (
        guild_id,
        vc_creator_id
    )

    row = fetch_one(
        query = query,
        values = values
    )

    if row is None:
        return None

    return _build_auto_vc_settings(row)


def get_auto_vc_moderator_role_ids(auto_vc_id: int) -> list[int]:
    query = '''
        SELECT role_id
        FROM auto_vc_moderator_roles
        WHERE auto_vc_id = %s
        ORDER BY role_id
    '''

    values = (
        auto_vc_id,
    )

    rows = fetch_all(
        query = query,
        values = values
    )

    return [
        int(row['role_id'])
        for row in rows
    ]


def get_vc_creator_id(auto_vc_id: int) -> int | None:
    settings = get_auto_vc_settings(
        auto_vc_id = auto_vc_id
    )

    if settings is None:
        return None

    return settings.vc_creator_id


def get_vc_category_id(auto_vc_id: int) -> int | None:
    settings = get_auto_vc_settings(
        auto_vc_id = auto_vc_id
    )

    if settings is None:
        return None

    return settings.vc_category_id


def get_member_role_id(auto_vc_id: int) -> int | None:
    settings = get_auto_vc_settings(
        auto_vc_id = auto_vc_id
    )

    if settings is None:
        return None

    return settings.member_role_id


def get_moderator_role_ids(auto_vc_id: int) -> list[int]:
    return get_auto_vc_moderator_role_ids(
        auto_vc_id = auto_vc_id
    )


def set_auto_vc_name(
    auto_vc_id: int,
    name: str
) -> None:
    query = '''
        UPDATE auto_vc_settings
        SET name = %s
        WHERE id = %s
    '''

    values = (
        name,
        auto_vc_id
    )

    execute(
        query = query,
        values = values
    )


def set_vc_creator(
    auto_vc_id: int,
    vc_creator_id: int | None
) -> None:
    query = '''
        UPDATE auto_vc_settings
        SET vc_creator_id = %s
        WHERE id = %s
    '''

    values = (
        vc_creator_id,
        auto_vc_id
    )

    execute(
        query = query,
        values = values
    )


def set_vc_category(
    auto_vc_id: int,
    vc_category_id: int | None
) -> None:
    query = '''
        UPDATE auto_vc_settings
        SET vc_category_id = %s
        WHERE id = %s
    '''

    values = (
        vc_category_id,
        auto_vc_id
    )

    execute(
        query = query,
        values = values
    )


def set_member_role(
    auto_vc_id: int,
    member_role_id: int | None
) -> None:
    query = '''
        UPDATE auto_vc_settings
        SET member_role_id = %s
        WHERE id = %s
    '''

    values = (
        member_role_id,
        auto_vc_id
    )

    execute(
        query = query,
        values = values
    )


def set_moderator_roles(
    auto_vc_id: int,
    role_ids: list[int]
) -> None:
    unique_role_ids = sorted(set(role_ids))

    query = '''
        DELETE FROM auto_vc_moderator_roles
        WHERE auto_vc_id = %s
    '''

    values = (
        auto_vc_id,
    )

    execute(
        query = query,
        values = values
    )

    if not unique_role_ids:
        return

    query = '''
        INSERT INTO auto_vc_moderator_roles (
            auto_vc_id,
            role_id
        )
        VALUES (%s, %s)
    '''

    values = [
        (
            auto_vc_id,
            role_id
        )
        for role_id in unique_role_ids
    ]

    execute_many(
        query = query,
        values = values
    )


def set_channel_name_template(
    auto_vc_id: int,
    channel_name_template: str
) -> None:
    query = '''
        UPDATE auto_vc_settings
        SET channel_name_template = %s
        WHERE id = %s
    '''

    values = (
        channel_name_template,
        auto_vc_id
    )

    execute(
        query = query,
        values = values
    )


def set_auto_vc_enabled(
    auto_vc_id: int,
    is_enabled: bool
) -> None:
    query = '''
        UPDATE auto_vc_settings
        SET is_enabled = %s
        WHERE id = %s
    '''

    values = (
        is_enabled,
        auto_vc_id
    )

    execute(
        query = query,
        values = values
    )


def toggle_auto_vc_enabled(auto_vc_id: int) -> bool | None:
    settings = get_auto_vc_settings(
        auto_vc_id = auto_vc_id
    )

    if settings is None:
        return None

    new_enabled = not settings.is_enabled

    set_auto_vc_enabled(
        auto_vc_id = auto_vc_id,
        is_enabled = new_enabled
    )

    return new_enabled


def set_auto_vc_position(
    auto_vc_id: int,
    position: int
) -> None:
    query = '''
        UPDATE auto_vc_settings
        SET position = %s
        WHERE id = %s
    '''

    values = (
        position,
        auto_vc_id
    )

    execute(
        query = query,
        values = values
    )


def set_default_auto_vc(auto_vc_id: int) -> bool:
    settings = get_auto_vc_settings(
        auto_vc_id = auto_vc_id
    )

    if settings is None:
        return False

    query = '''
        UPDATE auto_vc_settings
        SET is_default = FALSE
        WHERE guild_id = %s
    '''

    values = (
        settings.guild_id,
    )

    execute(
        query = query,
        values = values
    )

    query = '''
        UPDATE auto_vc_settings
        SET is_default = TRUE
        WHERE id = %s
    '''

    values = (
        auto_vc_id,
    )

    execute(
        query = query,
        values = values
    )

    return True


def delete_auto_vc_settings(auto_vc_id: int) -> tuple[bool, str]:
    settings = get_auto_vc_settings(
        auto_vc_id = auto_vc_id
    )

    if settings is None:
        return False, 'That Auto VC setup does not exist.'

    if settings.is_default and count_auto_vc_settings(settings.guild_id) > 1:
        return False, 'The default Auto VC setup cannot be deleted while other setups exist.'

    query = '''
        DELETE FROM auto_vc_settings
        WHERE id = %s
    '''

    values = (
        auto_vc_id,
    )

    execute(
        query = query,
        values = values
    )

    return True, 'Auto VC setup deleted.'


def delete_all_auto_vc_settings_for_guild(guild_id: int) -> None:
    query = '''
        DELETE FROM auto_vc_settings
        WHERE guild_id = %s
    '''

    values = (
        guild_id,
    )

    execute(
        query = query,
        values = values
    )