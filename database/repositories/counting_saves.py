from .base import fetch_one, execute, execute_get_rowcount


def get_user_save_balance(user_id: int) -> int:
    query = '''
        SELECT balance
        FROM user_counting_saves
        WHERE user_id = %s
    '''

    values = (
        user_id,
    )

    row = fetch_one(
        query = query,
        values = values
    )

    if row is None:
        return 0

    return int(row['balance'])


def credit_user_saves(user_id: int, amount: int) -> None:
    query = '''
        INSERT INTO user_counting_saves (user_id, balance)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE
            balance = balance + VALUES(balance)
    '''

    values = (
        user_id,
        amount
    )

    execute(
        query = query,
        values = values
    )


def consume_user_save_if_available(user_id: int) -> bool:
    query = '''
        UPDATE user_counting_saves
        SET balance = balance - 1
        WHERE user_id = %s AND balance > 0
    '''

    values = (
        user_id,
    )

    rowcount = execute_get_rowcount(
        query = query,
        values = values
    )

    return rowcount == 1


def record_entitlement_credit(
    entitlement_id: int,
    user_id: int,
    sku_id: int,
    saves_granted: int
) -> bool:
    """Idempotently records that an entitlement has been credited.

    Returns True the first time this entitlement_id is recorded, False if
    it had already been recorded before - callers use this to avoid
    double-crediting a user if the same purchase event is ever seen twice
    (e.g. a missed-event reconciliation sync re-observing it).
    """
    query = '''
        INSERT IGNORE INTO counting_save_purchases (
            entitlement_id,
            user_id,
            sku_id,
            saves_granted
        )
        VALUES (%s, %s, %s, %s)
    '''

    values = (
        entitlement_id,
        user_id,
        sku_id,
        saves_granted
    )

    rowcount = execute_get_rowcount(
        query = query,
        values = values
    )

    return rowcount == 1
