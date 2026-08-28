"""
Exercises premium entitlement edge cases directly, without needing Discord
to actually produce them - useful for the scenarios real test entitlements
can't simulate (they have no ends_at, so "expired via timestamp" and
"refunded while ends_at is still in the future" can't happen with them).

This calls the exact same handler functions the bot's gateway listeners
call (services.premium.handle_premium_entitlement_update/_delete), just
with a hand-built fake entitlement instead of a real one from Discord.

Only ever runs against the DEV database - refuses to run otherwise.

Usage:
    TEST_GUILD_ID=<your dev test guild id> python scripts/test_premium_scenarios.py --dev
"""

import asyncio
import os
import sys

from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from settings import settings

from database.repositories import guild_has_premium_cached, clear_guild_premium_status

from services.premium import (
    handle_premium_entitlement_update,
    handle_premium_entitlement_delete
)


@dataclass
class FakeEntitlement:
    id: int
    sku_id: int
    guild_id: int | None = None
    user_id: int | None = None
    deleted: bool = False
    ends_at: datetime | None = None


def _get_test_guild_id() -> int:
    raw = os.environ.get('TEST_GUILD_ID')

    if not raw:
        print(
            'Set TEST_GUILD_ID to a guild you own/control before running this.\n'
            'Example: TEST_GUILD_ID=123456789012345678 python scripts/test_premium_scenarios.py --dev',
            file = sys.stderr
        )
        sys.exit(1)

    return int(raw)


async def _run_scenario(
    name: str,
    guild_id: int,
    entitlement: FakeEntitlement,
    handler,
    expected_premium: bool
) -> bool:
    await handler(entitlement = entitlement)

    actual = guild_has_premium_cached(guild_id)
    passed = actual == expected_premium

    status = 'PASS' if passed else 'FAIL'
    print(f'[{status}] {name} -> premium is now {actual} (expected {expected_premium})')

    return passed


async def main() -> None:
    if not settings.dev:
        print('Refusing to run against production - pass --dev.', file = sys.stderr)
        sys.exit(1)

    guild_id = _get_test_guild_id()
    sku_id = settings.synto_premium_sku_id

    now = datetime.now(UTC)
    far_future = now + timedelta(days = 300)
    past = now - timedelta(days = 1)

    results = []

    # 1. Normal activation - lifetime entitlement, no ends_at (e.g. a real
    #    test entitlement, or a subscription with no fixed end date).
    results.append(await _run_scenario(
        'activate (create, no ends_at)',
        guild_id,
        FakeEntitlement(id = 1, sku_id = sku_id, guild_id = guild_id, deleted = False, ends_at = None),
        handle_premium_entitlement_update,
        expected_premium = True
    ))

    # 2. THE BUG THIS SESSION FIXED: an ENTITLEMENT_DELETE (refund/revoke)
    #    arrives while ends_at is still far in the future and deleted=False.
    #    Before the fix, this would have been treated as still active.
    results.append(await _run_scenario(
        'refund mid-subscription (delete, ends_at far in future)',
        guild_id,
        FakeEntitlement(id = 1, sku_id = sku_id, guild_id = guild_id, deleted = False, ends_at = far_future),
        handle_premium_entitlement_delete,
        expected_premium = False
    ))

    # 3. Re-activate so the next scenario starts from a known state.
    results.append(await _run_scenario(
        're-activate before expiry test',
        guild_id,
        FakeEntitlement(id = 2, sku_id = sku_id, guild_id = guild_id, deleted = False, ends_at = far_future),
        handle_premium_entitlement_update,
        expected_premium = True
    ))

    # 4. Natural expiry: an ENTITLEMENT_UPDATE with ends_at now in the past
    #    (this is what Discord sends when a subscription simply lapses,
    #    as opposed to being deleted/refunded).
    results.append(await _run_scenario(
        'natural expiry (update, ends_at in the past)',
        guild_id,
        FakeEntitlement(id = 2, sku_id = sku_id, guild_id = guild_id, deleted = False, ends_at = past),
        handle_premium_entitlement_update,
        expected_premium = False
    ))

    # 5. Renewal: an ENTITLEMENT_UPDATE with a new, later ends_at should
    #    bring premium back.
    results.append(await _run_scenario(
        'renewal (update, new future ends_at)',
        guild_id,
        FakeEntitlement(id = 2, sku_id = sku_id, guild_id = guild_id, deleted = False, ends_at = far_future),
        handle_premium_entitlement_update,
        expected_premium = True
    ))

    # 6. A wrong-SKU entitlement (e.g. a counting-saves purchase) must be
    #    ignored entirely - premium should stay exactly as it was.
    before = guild_has_premium_cached(guild_id)
    await handle_premium_entitlement_update(
        entitlement = FakeEntitlement(id = 3, sku_id = sku_id + 1, guild_id = guild_id, deleted = False, ends_at = None)
    )
    after = guild_has_premium_cached(guild_id)
    passed = before == after
    print(f'[{"PASS" if passed else "FAIL"}] unrelated SKU is ignored -> premium unchanged ({after})')
    results.append(passed)

    # Cleanup - don't leave the test guild premium-active.
    clear_guild_premium_status(guild_id = guild_id)

    print()
    if all(results):
        print(f'All {len(results)} scenarios passed.')
    else:
        failed = len(results) - sum(results)
        print(f'{failed}/{len(results)} scenario(s) FAILED - see above.')
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
