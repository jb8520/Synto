from datetime import datetime

from .base import execute, fetch_all, fetch_one, ensure_guild_exists


def set_guild_premium_status(
    guild_id: int,
    is_premium: bool,
    entitlement_id: int | None = None,
    sku_id: int | None = None,
    premium_ends_at: datetime | None = None
) -> None:
    ensure_guild_exists(guild_id)

    query = '''
        INSERT INTO guild_premium_status (
            guild_id,
            is_premium,
            entitlement_id,
            sku_id,
            premium_ends_at
        )
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            is_premium = VALUES(is_premium),
            entitlement_id = VALUES(entitlement_id),
            sku_id = VALUES(sku_id),
            premium_ends_at = VALUES(premium_ends_at)
    '''

    values = (
        guild_id,
        is_premium,
        entitlement_id,
        sku_id,
        premium_ends_at
    )

    execute(
        query = query,
        values = values
    )


def clear_guild_premium_status(guild_id: int) -> None:
    set_guild_premium_status(
        guild_id = guild_id,
        is_premium = False,
        entitlement_id = None,
        sku_id = None,
        premium_ends_at = None
    )


def guild_has_premium_cached(guild_id: int) -> bool:
    query = '''
        SELECT is_premium
        FROM guild_premium_status
        WHERE guild_id = %s
        LIMIT 1
    '''

    row = fetch_one(
        query = query,
        values = (guild_id,)
    )

    if row is None:
        return False

    return bool(row['is_premium'])


def get_cached_premium_guild_ids() -> set[int]:
    query = '''
        SELECT guild_id
        FROM guild_premium_status
        WHERE is_premium = TRUE
    '''

    rows = fetch_all(query = query)

    return {
        int(row['guild_id'])
        for row in rows
    }


def set_many_guilds_not_premium(guild_ids: set[int]) -> None:
    for guild_id in guild_ids:
        clear_guild_premium_status(
            guild_id = guild_id
        )