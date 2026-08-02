import json

from datetime import datetime
from typing import Any

from ..models import Metrics

from .base import execute, fetch_all, fetch_one


def _row_to_metric(row: dict[str, Any]) -> Metrics:
    details = row['details']

    if isinstance(details, str):
        details = json.loads(details)

    return Metrics(
        id = int(row['id']),
        user_id = int(row['user_id']),
        guild_id = int(row['guild_id']),
        timestamp = row['timestamp'],
        action_type = str(row['action_type']),
        command_name = row['command_name'],
        auto_vc_type = row['auto_vc_type'],
        details = details
    )


def _log_metric(
    user_id: int,
    guild_id: int,
    action_type: str,
    command_name: str | None = None,
    auto_vc_type: str | None = None,
    details: dict[str, Any] | None = None,
    timestamp: datetime | None = None
) -> None:
    query = '''
        INSERT INTO metrics (
            user_id,
            guild_id,
            timestamp,
            action_type,
            command_name, 
            auto_vc_type,
            details
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''

    values = (
        user_id,
        guild_id,
        timestamp if timestamp is not None else datetime.now(),
        action_type,
        command_name,
        auto_vc_type,
        json.dumps(details) if details is not None else None
    )
    
    execute(
        query = query,
        values = values
    )


def log_command(
    user_id: int,
    guild_id: int,
    command_name: str,
    timestamp: datetime | None = None,
    details: dict[str, Any] | None = None
) -> None:
    _log_metric(
        user_id = user_id,
        guild_id = guild_id,
        action_type = 'command_run',
        command_name = command_name,
        details = details,
        timestamp = timestamp
    )

def log_auto_vc(
    user_id: int,
    guild_id: int,
    auto_vc_type: str,
    timestamp: datetime | None = None,
    details: dict[str, Any] | None = None
) -> None:
    _log_metric(
        user_id = user_id,
        guild_id = guild_id,
        action_type = 'auto_vc',
        auto_vc_type = auto_vc_type,
        details = details,
        timestamp = timestamp
    )

def log_welcome_message(
    user_id: int,
    guild_id: int,
    timestamp: datetime | None = None,
    details: dict[str, Any] | None = None
) -> None:
    _log_metric(
        user_id = user_id,
        guild_id = guild_id,
        action_type = 'welcome_message',
        details = details,
        timestamp = timestamp
    )

def log_counting(
    user_id: int,
    guild_id: int,
    timestamp: datetime | None = None,
    details: dict[str, Any] | None = None
) -> None:
    _log_metric(
        user_id = user_id,
        guild_id = guild_id,
        action_type = 'counting_action',
        details = details,
        timestamp = timestamp
    )

def log_game(
    user_id: int,
    guild_id: int,
    game_name: str | None = None,
    timestamp: datetime | None = None,
    details: dict[str, Any] | None = None
) -> None:
    if details is None:
        details = {}

    if game_name is not None:
        details['game_name'] = game_name

    _log_metric(
        user_id = user_id,
        guild_id = guild_id,
        action_type = 'game_run',
        details = details,
        timestamp = timestamp
    )


def _get_conditions(
    guild_id: int | None = None,
    user_id: int | None = None,
    action_type: str | None = None
) -> tuple[str, list[Any]]:
    conditions = []
    
    values: list[Any] = []

    if guild_id is not None:
        conditions.append('guild_id = %s')
        values.append(guild_id)

    if user_id is not None:
        conditions.append('user_id = %s')
        values.append(user_id)

    if action_type is not None:
        conditions.append('action_type = %s')
        values.append(action_type)

    where_clause = ''

    if len(conditions) > 0:
        where_clause = 'WHERE ' + ' AND '.join(conditions)

    return where_clause, values

def get_recent_metrics(
    limit: int = 50,
    guild_id: int | None = None,
    user_id: int | None = None,
    action_type: str | None = None
) -> list[Metrics]:
    where_clause, values = _get_conditions(
        guild_id = guild_id,
        user_id = user_id,
        action_type = action_type
    )

    values.append(limit)

    query = f'''
        SELECT
            id,
            user_id,
            guild_id,
            timestamp,
            action_type,
            command_name,
            auto_vc_type,
            details
        FROM metrics
        {where_clause}
        ORDER BY timestamp DESC
        LIMIT %s
    '''

    values = tuple(values)
    
    rows = fetch_all(
        query = query,
        values = values
    )

    return [_row_to_metric(row) for row in rows]

def count_metrics(
    guild_id: int | None = None,
    user_id: int | None = None,
    action_type: str | None = None
) -> int:
    where_clause, values = _get_conditions(
        guild_id = guild_id,
        user_id = user_id,
        action_type = action_type
    )
    
    query = f'\
        SELECT COUNT(*) AS metric_count \
        FROM metrics \
        {where_clause} \
    '

    values = tuple(values)

    row = fetch_one(
        query = query,
        values = values,
    )

    return int(row['metric_count'])