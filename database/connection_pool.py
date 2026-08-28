from contextlib import contextmanager

from typing import Iterator

from mysql.connector import pooling
from mysql.connector.connection import MySQLConnection

from settings import settings


class DatabaseConnectionError(Exception):
    def __init__(self):
        self.message = '❌ A connection to the database could not be established.' 
        super().__init__(self.message)


# --- Create the pool once at startup ---
try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name = 'synto_pool',
        pool_size = 10,
        pool_reset_session = True,

        host = settings.database_host,
        database = settings.database_name,
        user = settings.database_user,
        password = settings.database_password
    )

except Exception as e:
    raise DatabaseConnectionError() from e


@contextmanager
def _get_connection() -> Iterator[MySQLConnection]:
    connection = connection_pool.get_connection()
    
    try:
        yield connection

    finally:
        connection.close()