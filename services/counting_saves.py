import discord

from discord.ext import commands

from settings import settings

from database.repositories import (
    credit_user_saves,
    get_user_save_balance,
    record_entitlement_credit
)


def _get_save_pack_size(sku_id: int) -> int | None:
    if sku_id == settings.counting_save_1_sku_id:
        return 1

    if sku_id == settings.counting_save_3_sku_id:
        return 3

    if sku_id == settings.counting_save_10_sku_id:
        return 10

    return None


async def _notify_user_of_credit(
    bot: commands.Bot,
    user_id: int,
    pack_size: int,
    new_balance: int
) -> None:
    # Premium/SKU purchase buttons don't route through our interaction
    # handlers at all (that's why they have no callback) - Discord's
    # purchase flow is entirely client-side, so there's no original
    # message we can go back and edit with the new balance. A DM is the
    # only reliable way to confirm the purchase landed.
    try:
        user = bot.get_user(user_id) or await bot.fetch_user(user_id)

        await user.send(
            f'✅ Your purchase of `{pack_size}` Counting Save{"s" if pack_size != 1 else ""} was successful! '
            f'You now have `{new_balance}` Counting Save{"s" if new_balance != 1 else ""}.'
        )

    except discord.HTTPException:
        pass  # DMs closed or user unreachable - the balance is still credited correctly


async def handle_counting_save_entitlement(
    entitlement: discord.Entitlement,
    bot: commands.Bot | None = None
) -> None:
    pack_size = _get_save_pack_size(int(entitlement.sku_id))

    if pack_size is None:
        return

    user_id = getattr(entitlement, 'user_id', None)

    if user_id is None:
        return

    # Each consumable purchase is exactly one entitlement - there's no
    # quantity field, so the pack size comes from which SKU was bought.
    # The ledger insert is the idempotency guard: if this entitlement was
    # already credited (e.g. seen again by the reconciliation sync), this
    # returns False and we skip crediting/consuming it a second time.
    newly_recorded = record_entitlement_credit(
        entitlement_id = int(entitlement.id),
        user_id = int(user_id),
        sku_id = int(entitlement.sku_id),
        saves_granted = pack_size
    )

    if not newly_recorded:
        return

    credit_user_saves(
        user_id = int(user_id),
        amount = pack_size
    )

    new_balance = get_user_save_balance(int(user_id))

    print(f'✅ Credited {pack_size} Counting Save(s) to user_id={user_id}')

    if bot is not None:
        await _notify_user_of_credit(
            bot = bot,
            user_id = int(user_id),
            pack_size = pack_size,
            new_balance = new_balance
        )

    try:
        await entitlement.consume()

    except discord.HTTPException as error:
        # The balance is already credited and the ledger already recorded
        # it, so a failed consume() here doesn't cost the user anything -
        # it just means the entitlement will still show as unconsumed on
        # Discord's side, which is harmless since our ledger prevents any
        # future re-credit for this same entitlement_id.
        print(
            f'⚠️ Failed to consume Counting Save entitlement {entitlement.id}\n'
            f'{type(error).__name__}: {error}'
        )


async def sync_counting_save_entitlements(bot: commands.Bot) -> None:
    print('🔄 Syncing Counting Save entitlements...')

    sku_ids = [
        settings.counting_save_1_sku_id,
        settings.counting_save_3_sku_id,
        settings.counting_save_10_sku_id
    ]

    try:
        async for entitlement in bot.entitlements(
            skus = [discord.Object(id = sku_id) for sku_id in sku_ids],
            exclude_ended = False,
            exclude_deleted = True
        ):
            if entitlement.consumed:
                continue

            await handle_counting_save_entitlement(entitlement = entitlement, bot = bot)

    except Exception as error:
        print(
            '❌ Failed to sync Counting Save entitlements\n'
            f'{type(error).__name__}: {error}'
        )
        return

    print('✅ Counting Save entitlement sync complete')
