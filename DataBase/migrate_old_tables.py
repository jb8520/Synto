import os
from typing import Iterable

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host = os.environ['DATABASE_HOST'],
        user = os.environ['DATABASE_USER'],
        password = os.environ['DATABASE_PASSWORD'],
        database = os.environ['DATABASE_NAME'],
    )


def to_int(
    value,
    default: int = 0
) -> int:
    if value is None:
        return default

    value = str(value).strip()

    if value == '' or value.lower() == 'none':
        return default

    return int(value)


def to_optional_int(value) -> int | None:
    value = to_int(value)

    if value == 0:
        return None

    return value


def to_bool(value) -> int:
    if value is None:
        return 0

    value = str(value).strip().lower()

    return 1 if value in ('true', '1', 'yes', 'on') else 0


def none_if_fake_none(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == '' or value.lower() == 'none':
        return None

    return value


def clean_hex_colour(value):
    value = none_if_fake_none(value)

    if value is None:
        return None

    if value.startswith('#'):
        value = value[1:]

    value = value.upper()

    if len(value) != 6:
        return None

    try:
        int(value, 16)

    except ValueError:
        return None

    return value


def split_role_ids(value) -> list[int]:
    value = none_if_fake_none(value)

    if value is None:
        return []

    role_ids = []

    for bit in str(value).split(','):
        bit = bit.strip()

        if bit in ('', '0'):
            continue

        try:
            role_ids.append(int(bit))

        except ValueError:
            print(f'Skipping invalid role ID: {bit!r}')

    return sorted(set(role_ids))


def upsert_guilds(
    cursor,
    guild_ids: Iterable[int]
) -> None:
    for guild_id in sorted(set(guild_ids)):
        if guild_id == 0:
            continue

        cursor.execute(
            '''
            INSERT IGNORE INTO guilds (guild_id)
            VALUES (%s)
            ''',
            (guild_id,),
        )


def collect_guild_ids(cursor) -> set[int]:
    guild_ids: set[int] = set()

    table_queries = [
        ('Auto_Vc', 'guild_id'),
        ('Counting', 'guild_id'),
        ('Welcome_Message', 'guild_id'),
        ('Metrics', 'guild_id'),
    ]

    for table_name, column_name in table_queries:
        try:
            cursor.execute(
                f'''
                SELECT DISTINCT {column_name}
                FROM {table_name}
                '''
            )

        except mysql.connector.Error as error:
            print(f'Skipping {table_name}: {error}')
            continue

        for (guild_id,) in cursor.fetchall():
            guild_id = to_int(guild_id)

            if guild_id != 0:
                guild_ids.add(guild_id)

    return guild_ids


def get_or_create_legacy_auto_vc_settings(
    cursor,
    guild_id: int,
    vc_creator_id: int | None,
    vc_category_id: int | None,
    member_role_id: int | None
) -> int:
    cursor.execute(
        '''
        SELECT id
        FROM auto_vc_settings
        WHERE
            guild_id = %s
            AND is_default = TRUE
        LIMIT 1
        ''',
        (guild_id,),
    )

    row = cursor.fetchone()

    if row is not None:
        auto_vc_id = int(row[0])

        cursor.execute(
            '''
            UPDATE auto_vc_settings
            SET
                name = %s,
                vc_creator_id = %s,
                vc_category_id = %s,
                member_role_id = %s,
                is_enabled = TRUE,
                is_default = TRUE,
                position = 1,
                channel_name_template = %s
            WHERE id = %s
            ''',
            (
                'VC',
                vc_creator_id,
                vc_category_id,
                member_role_id,
                '{name} {number}',
                auto_vc_id,
            ),
        )

        return auto_vc_id

    cursor.execute(
        '''
        INSERT INTO auto_vc_settings (
            guild_id,
            name,
            vc_creator_id,
            vc_category_id,
            member_role_id,
            is_enabled,
            is_default,
            position,
            channel_name_template
        )
        VALUES (%s, %s, %s, %s, %s, TRUE, TRUE, 1, %s)
        ''',
        (
            guild_id,
            'VC',
            vc_creator_id,
            vc_category_id,
            member_role_id,
            '{name} {number}',
        ),
    )

    return int(cursor.lastrowid)


def migrate_auto_vc(cursor) -> None:
    cursor.execute(
        '''
        SELECT guild_id, vc_creator_id, vc_category_id, member_role, bypass_roles
        FROM Auto_Vc
        '''
    )

    rows = cursor.fetchall()

    for guild_id, vc_creator_id, vc_category_id, member_role, bypass_roles in rows:
        guild_id = to_int(guild_id)

        if guild_id == 0:
            continue

        auto_vc_id = get_or_create_legacy_auto_vc_settings(
            cursor = cursor,
            guild_id = guild_id,
            vc_creator_id = to_optional_int(vc_creator_id),
            vc_category_id = to_optional_int(vc_category_id),
            member_role_id = to_optional_int(member_role),
        )

        cursor.execute(
            '''
            DELETE FROM auto_vc_moderator_roles
            WHERE auto_vc_id = %s
            ''',
            (auto_vc_id,),
        )

        for role_id in split_role_ids(bypass_roles):
            cursor.execute(
                '''
                INSERT IGNORE INTO auto_vc_moderator_roles (
                    auto_vc_id,
                    role_id
                )
                VALUES (%s, %s)
                ''',
                (
                    auto_vc_id,
                    role_id,
                ),
            )


def migrate_counting(cursor) -> None:
    cursor.execute(
        '''
        SELECT guild_id, channel_id, highscore, current_score, message_id, author_id, double_count
        FROM Counting
        '''
    )

    rows = cursor.fetchall()

    for guild_id, channel_id, highscore, current_score, message_id, author_id, double_count in rows:
        guild_id = to_int(guild_id)

        if guild_id == 0:
            continue

        cursor.execute(
            '''
            INSERT INTO counting_settings (
                guild_id,
                channel_id,
                highscore,
                current_score,
                last_message_id,
                last_author_id,
                double_count
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                channel_id = VALUES(channel_id),
                highscore = VALUES(highscore),
                current_score = VALUES(current_score),
                last_message_id = VALUES(last_message_id),
                last_author_id = VALUES(last_author_id),
                double_count = VALUES(double_count)
            ''',
            (
                guild_id,
                to_int(channel_id),
                to_int(highscore),
                to_int(current_score),
                to_int(message_id),
                to_int(author_id),
                to_bool(double_count),
            ),
        )


def migrate_welcome_message(cursor) -> None:
    cursor.execute(
        '''
        SELECT guild_id, channel_id, title, description, colour, activated
        FROM Welcome_Message
        '''
    )

    rows = cursor.fetchall()

    for guild_id, channel_id, title, description, colour, activated in rows:
        guild_id = to_int(guild_id)

        if guild_id == 0:
            continue

        title = none_if_fake_none(title) or 'Welcome!'

        cursor.execute(
            '''
            INSERT INTO welcome_message_settings (
                guild_id,
                channel_id,
                title,
                description,
                colour,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                channel_id = VALUES(channel_id),
                title = VALUES(title),
                description = VALUES(description),
                colour = VALUES(colour),
                status = VALUES(status)
            ''',
            (
                guild_id,
                to_int(channel_id),
                str(title)[:256],
                none_if_fake_none(description),
                clean_hex_colour(colour),
                to_bool(activated),
            ),
        )


def migrate_metrics(cursor) -> None:
    cursor.execute(
        '''
        SELECT id, user_id, guild_id, timestamp, action_type, command_name, auto_vc_type, details
        FROM Metrics
        '''
    )

    rows = cursor.fetchall()

    for id_, user_id, guild_id, timestamp, action_type, command_name, auto_vc_type, details in rows:
        guild_id = to_int(guild_id)

        if guild_id == 0:
            continue

        cursor.execute(
            '''
            INSERT INTO metrics (
                id,
                user_id,
                guild_id,
                timestamp,
                action_type,
                command_name,
                auto_vc_type,
                details
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                user_id = VALUES(user_id),
                guild_id = VALUES(guild_id),
                timestamp = VALUES(timestamp),
                action_type = VALUES(action_type),
                command_name = VALUES(command_name),
                auto_vc_type = VALUES(auto_vc_type),
                details = VALUES(details)
            ''',
            (
                to_int(id_),
                to_int(user_id),
                guild_id,
                timestamp,
                str(action_type),
                none_if_fake_none(command_name),
                none_if_fake_none(auto_vc_type),
                details,
            ),
        )


def main():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        print('Starting migration...')

        guild_ids = collect_guild_ids(cursor)
        upsert_guilds(cursor, guild_ids)

        print(f'Updated guilds table: {len(guild_ids)} guilds')

        migrate_auto_vc(cursor)
        print('Migrated Auto_Vc')

        migrate_counting(cursor)
        print('Migrated Counting')

        migrate_welcome_message(cursor)
        print('Migrated Welcome_Message')

        migrate_metrics(cursor)
        print('Migrated Metrics')

        connection.commit()
        print('Migration complete.')

    except Exception:
        connection.rollback()
        print('Migration failed. Rolled back changes.')
        raise

    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    main()