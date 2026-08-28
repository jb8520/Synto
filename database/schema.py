from database.connection_pool import _get_connection


def _column_exists(cursor, table_name: str, column_name: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = %s
            AND COLUMN_NAME = %s
        """,
        (table_name, column_name)
    )

    (count,) = cursor.fetchone()

    return count > 0


def create_tables() -> None:
    with _get_connection() as connection:
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS guilds (
                    guild_id BIGINT UNSIGNED PRIMARY KEY,
                    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS guild_premium_status (
                    guild_id BIGINT UNSIGNED PRIMARY KEY,

                    is_premium BOOLEAN NOT NULL DEFAULT FALSE,

                    entitlement_id BIGINT UNSIGNED NULL,
                    sku_id BIGINT UNSIGNED NULL,
                    purchaser_user_id BIGINT UNSIGNED NULL,
                    premium_ends_at TIMESTAMP NULL,

                    last_checked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,

                    FOREIGN KEY (guild_id)
                        REFERENCES guilds(guild_id)
                        ON DELETE CASCADE
                )
                """
            )

            if not _column_exists(cursor, 'guild_premium_status', 'purchaser_user_id'):
                cursor.execute(
                    """
                    ALTER TABLE guild_premium_status
                    ADD COLUMN purchaser_user_id BIGINT UNSIGNED NULL
                    """
                )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS counting_settings (
                    guild_id BIGINT UNSIGNED PRIMARY KEY,
                    channel_id BIGINT UNSIGNED NOT NULL DEFAULT 0,
                    highscore INT UNSIGNED NOT NULL DEFAULT 0,
                    current_score INT UNSIGNED NOT NULL DEFAULT 0,
                    last_message_id BIGINT UNSIGNED NOT NULL DEFAULT 0,
                    last_author_id BIGINT UNSIGNED NOT NULL DEFAULT 0,
                    double_count BOOLEAN NOT NULL DEFAULT FALSE,

                    FOREIGN KEY (guild_id)
                        REFERENCES guilds(guild_id)
                        ON DELETE CASCADE
                )
                """
            )

            if not _column_exists(cursor, 'counting_settings', 'counting_saves_enabled'):
                cursor.execute(
                    """
                    ALTER TABLE counting_settings
                    ADD COLUMN counting_saves_enabled BOOLEAN NOT NULL DEFAULT TRUE
                    """
                )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_counting_saves (
                    user_id BIGINT UNSIGNED PRIMARY KEY,
                    balance INT UNSIGNED NOT NULL DEFAULT 0
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS counting_save_purchases (
                    entitlement_id BIGINT UNSIGNED PRIMARY KEY,

                    user_id BIGINT UNSIGNED NOT NULL,
                    sku_id BIGINT UNSIGNED NOT NULL,
                    saves_granted INT UNSIGNED NOT NULL,

                    credited_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

                    INDEX idx_counting_save_purchases_user (user_id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS auto_vc_settings (
                    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

                    guild_id BIGINT UNSIGNED NOT NULL,

                    name VARCHAR(50) NOT NULL DEFAULT 'VC',

                    vc_creator_id BIGINT UNSIGNED NULL,
                    vc_category_id BIGINT UNSIGNED NULL,
                    member_role_id BIGINT UNSIGNED NULL,

                    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
                    is_default BOOLEAN NOT NULL DEFAULT FALSE,

                    default_guild_id BIGINT UNSIGNED
                        GENERATED ALWAYS AS (
                            CASE WHEN is_default THEN guild_id ELSE NULL END
                        ) STORED,

                    position INT UNSIGNED NOT NULL DEFAULT 0,

                    channel_name_template VARCHAR(100) NOT NULL DEFAULT '{name} {number}',

                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

                    FOREIGN KEY (guild_id)
                        REFERENCES guilds(guild_id)
                        ON DELETE CASCADE,

                    UNIQUE KEY unique_auto_vc_creator_channel (guild_id, vc_creator_id),
                    UNIQUE KEY unique_default_auto_vc_per_guild (default_guild_id),

                    INDEX idx_auto_vc_guild_id (guild_id),
                    INDEX idx_auto_vc_guild_position (guild_id, position),
                    INDEX idx_auto_vc_creator_lookup (guild_id, vc_creator_id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS auto_vc_moderator_roles (
                    auto_vc_id BIGINT UNSIGNED NOT NULL,
                    role_id BIGINT UNSIGNED NOT NULL,

                    PRIMARY KEY (auto_vc_id, role_id),

                    FOREIGN KEY (auto_vc_id)
                        REFERENCES auto_vc_settings(id)
                        ON DELETE CASCADE
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS welcome_message_settings (
                    guild_id BIGINT UNSIGNED PRIMARY KEY,
                    channel_id BIGINT UNSIGNED NOT NULL DEFAULT 0,
                    title VARCHAR(256) NOT NULL DEFAULT 'Welcome!',
                    description TEXT NULL,
                    colour CHAR(6) NULL,
                    status BOOLEAN NOT NULL DEFAULT FALSE,

                    FOREIGN KEY (guild_id)
                        REFERENCES guilds(guild_id)
                        ON DELETE CASCADE
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS general_settings (
                    guild_id BIGINT UNSIGNED PRIMARY KEY,

                    auto_vc_enabled BOOLEAN NOT NULL DEFAULT TRUE,
                    counting_enabled BOOLEAN NOT NULL DEFAULT TRUE,
                    games_enabled BOOLEAN NOT NULL DEFAULT TRUE,

                    embed_colour CHAR(6) NULL,

                    updates_channel_id BIGINT UNSIGNED NOT NULL DEFAULT 0,

                    FOREIGN KEY (guild_id)
                        REFERENCES guilds(guild_id)
                        ON DELETE CASCADE
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS general_admin_roles (
                    guild_id BIGINT UNSIGNED NOT NULL,
                    role_id BIGINT UNSIGNED NOT NULL,

                    PRIMARY KEY (guild_id, role_id),

                    FOREIGN KEY (guild_id)
                        REFERENCES guilds(guild_id)
                        ON DELETE CASCADE
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT UNSIGNED NOT NULL,
                    guild_id BIGINT UNSIGNED NOT NULL,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    action_type VARCHAR(50) NOT NULL,
                    command_name VARCHAR(50) DEFAULT NULL,
                    auto_vc_type VARCHAR(50) DEFAULT NULL,
                    details JSON DEFAULT NULL,

                    INDEX idx_metrics_action_timestamp (action_type, timestamp),
                    INDEX idx_metrics_user_timestamp (user_id, timestamp),
                    INDEX idx_metrics_guild_timestamp (guild_id, timestamp)
                )
                """
            )

            connection.commit()

        finally:
            cursor.close()

if __name__ == '__main__':
    create_tables()