import os

from mysql.connector import pooling
from mysql.connector import errors as mysql_errors

from typing import Any, Tuple

from datetime import datetime

from dotenv import load_dotenv
load_dotenv()


class DatabaseConnectionFail(Exception):
    def __init__(self):
        self.message = '❌ A connection to the database could not be established.' 
        super().__init__(self.message)


# --- Create the pool once at startup ---
try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name = 'metrics_pool',
        pool_size = 5,
        pool_reset_session = True,
        host = os.environ['DATABASE_HOST'],
        user = os.environ['DATABASE_USER'],
        password = os.environ['DATABASE_PASSWORD'],
        database = os.environ['DATABASE_NAME']
    )

except Exception as e:
    raise DatabaseConnectionFail() from e



def _update_database(query: str, values: Tuple[Any, ...]):
    try:
        connection = connection_pool.get_connection()
    except mysql_errors.InterfaceError as e:
        raise DatabaseConnectionFail() from e

    try:
        cursor = connection.cursor()
        try:
            cursor.execute(
                operation=query,
                params=values
            )
            connection.commit()
        finally:
            cursor.close()
    finally:
        connection.close()


def _log_metric(user_id: int, guild_id: int, action_type: str, timestamp: datetime = None, **extra_fields):
    columns = ['user_id', 'guild_id', 'timestamp', 'action_type'] + list(extra_fields.keys())

    placeholders = ', '.join(['%s'] * len(columns))

    query = f"INSERT INTO Metrics({', '.join(columns)}) VALUES ({placeholders})"

    values = (
        user_id,
        guild_id,
        timestamp if timestamp is not None else datetime.now(),
        action_type,
        *extra_fields.values()
    )

    _update_database(
        query = query,
        values = values
    )



def log_command(user_id: int, guild_id: int, command_name: str, timestamp: datetime = None):
    _log_metric(
        user_id = user_id,
        guild_id = guild_id,
        action_type = 'command_run',
        timestamp = timestamp,
        command_name = command_name
    )


def log_auto_vc(user_id: int, guild_id: int, auto_vc_type: str, timestamp: datetime = None):
    _log_metric(
        user_id = user_id,
        guild_id = guild_id,
        action_type = 'auto_vc',
        timestamp = timestamp,
        auto_vc_type = auto_vc_type
    )
    

def log_welcome_message(user_id: int, guild_id: int, timestamp: datetime = None):
    _log_metric(
        user_id = user_id,
        guild_id = guild_id,
        action_type = 'welcome_message',
        timestamp = timestamp
    )


def log_counting(user_id: int, guild_id: int, timestamp: datetime = None):
    _log_metric(
        user_id = user_id,
        guild_id = guild_id,
        action_type = 'counting_action',
        timestamp = timestamp
    )


def log_games(user_id: int, guild_id: int, timestamp: datetime = None):
    _log_metric(
        user_id = user_id,
        guild_id = guild_id,
        action_type = 'game_run',
        timestamp = timestamp
    )