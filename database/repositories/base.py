from typing import Any, Iterable

from ..connection_pool import _get_connection


def fetch_one(
    query: str,
    values: Iterable[Any] = ()
):
    with _get_connection() as connection:
        cursor = connection.cursor(dictionary = True)

        try:
            cursor.execute(query, tuple(values))
            
            return cursor.fetchone()
        
        finally:
            cursor.close()


def fetch_all(
    query: str,
    values: Iterable[Any] = ()
):
    with _get_connection() as connection:
        cursor = connection.cursor(dictionary = True)

        try:
            cursor.execute(query, tuple(values))
        
            return cursor.fetchall()
        
        finally:
            cursor.close()


def execute(
    query: str,
    values: Iterable[Any] = ()
) -> Any | None:
    with _get_connection() as connection:
        cursor = connection.cursor()

        try:
            cursor.execute(query, tuple(values))
            
            connection.commit()
        
        finally:
            cursor.close()

        return cursor.lastrowid

def execute_get_rowcount(
    query: str,
    values: Iterable[Any] = ()
) -> int:
    with _get_connection() as connection:
        cursor = connection.cursor()

        try:
            cursor.execute(query, tuple(values))

            connection.commit()

            return cursor.rowcount

        finally:
            cursor.close()

def execute_many(
    query: str,
    values: Iterable[Iterable[Any]]
) -> None:
    value_rows = list(values)

    if len(value_rows) == 0:
        return
    
    with _get_connection() as connection:
        cursor = connection.cursor()

        try:
            cursor.executemany(query, value_rows)
        
            connection.commit()
        
        finally:
            cursor.close()


def ensure_guild_exists(guild_id: int) -> None:
    query = 'INSERT IGNORE INTO guilds (guild_id) VALUES (%s)'
    
    values = (
        guild_id,
    )
    
    execute(
        query = query,
        values = values
    )