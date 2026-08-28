import datetime
import discord

from discord import app_commands
from discord.ext import commands

from database.repositories import (
    log_command,
    clear_guild_premium_status,
    get_cached_premium_guild_ids,
    guild_has_premium_cached,
    set_guild_premium_status,
    set_many_guilds_not_premium,
    get_user_save_balance
)
from settings import settings
from ui.config import get_settings_colour
from ui.views.premium import (
    PremiumUpsellView,
    CountingSavesUpsellView
)


def _is_premium_sku(sku_id: int) -> bool:
    return sku_id == settings.synto_premium_sku_id


def _get_entitlement_guild_id(entitlement: discord.Entitlement) -> int | None:
    guild_id = getattr(entitlement, 'guild_id', None)

    if guild_id is None:
        return None

    return int(guild_id)

def _get_entitlement_user_id(entitlement: discord.Entitlement) -> int | None:
    user_id = getattr(entitlement, 'user_id', None)

    if user_id is None:
        return None

    return int(user_id)

def _entitlement_is_active(entitlement: discord.Entitlement) -> bool:
    deleted = getattr(entitlement, 'deleted', False)

    if deleted:
        return False

    ends_at = getattr(entitlement, 'ends_at', None)

    if ends_at is None:
        return True

    now = datetime.datetime.now(datetime.UTC)

    return ends_at > now


def build_premium_embed(
    interaction: discord.Interaction,
    has_premium: bool
) -> discord.Embed:
    if has_premium:
        description = (
            '✅ **Synto Premium is active for this server.**\n\n'
            'This server has access to premium features such as:\n'
            '> Multiple Auto VC setups\n'
            '> Premium configuration options\n'
            '> Future premium-only features'
        )

    else:
        description = (
            '✨ **Unlock Synto Premium for this server.**\n\n'
            'Premium currently unlocks:\n'
            '> Up to `5` Auto VC setups\n'
            '> More server configuration options\n'
            '> Priority support\n\n'
            'Use the button below to upgrade this server.'
        )

    embed = discord.Embed(
        title = 'Synto Premium',
        description = description,
        colour = get_settings_colour(interaction.guild.id)
    )

    embed.set_footer(
        text = f'Server: {interaction.guild.name}'
    )

    return embed


def build_counting_saves_embed(guild_id: int, balance: int) -> discord.Embed:
    embed = discord.Embed(
        title = 'Counting Saves',
        description = (
            'A Counting Save lets you rescue your own mistake before it ruins the count - '
            'if you post the wrong number or double count, you get 60 seconds to use one '
            'and keep the count going.\n\n'
            'Counting Saves belong to you, not a server - buy them once and use them in '
            'any server that has them enabled.\n\n'
            '**Available packs:**\n'
            '> `1` save\n'
            '> `3` saves\n'
            '> `10` saves\n\n'
            'Use the buttons below to buy saves.'
        ),
        colour = get_settings_colour(guild_id),
    )

    embed.add_field(
        name = 'Your Balance',
        value = f'> `{balance}` Counting Save{"s" if balance != 1 else ""}',
        inline = False
    )

    return embed


async def premium_upsell(interaction: discord.Interaction) -> None:
    if interaction.guild is None:
        await interaction.response.send_message(
            '❌ Premium can only be viewed inside a server.',
            ephemeral = True
        )
        return

    has_premium = guild_has_premium_cached(interaction.guild.id)

    embed = build_premium_embed(
        interaction = interaction,
        has_premium = has_premium
    )

    # send_message's `view` defaults to the MISSING sentinel, not None -
    # passing None explicitly makes discord.py call None.is_finished() and crash.
    view = discord.utils.MISSING if has_premium else PremiumUpsellView()

    await interaction.response.send_message(
        embed = embed,
        view = view
    )

    log_command(
        user_id = interaction.user.id,
        guild_id = interaction.guild.id,
        command_name = 'premium'
    )


async def premium_status(interaction: discord.Interaction) -> None:
    if interaction.guild is None:
        await interaction.response.send_message(
            '❌ Premium status can only be checked inside a server.',
            ephemeral = True
        )
        return

    has_premium = guild_has_premium_cached(interaction.guild.id)

    premium_entitlements = [
        entitlement
        for entitlement in interaction.entitlements
        if entitlement.sku_id == settings.synto_premium_sku_id
    ]

    if has_premium:
        status_text = '✅ Active'
    
    else:
        status_text = '❌ Not active'

    embed = discord.Embed(
        title = 'Premium Status',
        colour = get_settings_colour(interaction.guild.id)
    )

    embed.add_field(
        name = 'Synto Premium',
        value = f'> {status_text}',
        inline = False
    )

    embed.add_field(
        name = 'Premium Entitlements Found',
        value = f'> `{len(premium_entitlements)}`',
        inline = False
    )

    await interaction.response.send_message(
        embed = embed
    )

    log_command(
        user_id = interaction.user.id,
        guild_id = interaction.guild.id,
        command_name = 'premium_status'
    )


async def counting_saves_upsell(interaction: discord.Interaction) -> None:
    if interaction.guild is None:
        await interaction.response.send_message(
            '❌ Counting Saves can only be bought inside a server.',
            ephemeral = True
        )
        return

    balance = get_user_save_balance(interaction.user.id)

    await interaction.response.send_message(
        embed = build_counting_saves_embed(guild_id = interaction.guild.id, balance = balance),
        view = CountingSavesUpsellView()
    )

    log_command(
        user_id = interaction.user.id,
        guild_id = interaction.guild.id,
        command_name = 'counting_saves'
    )


async def handle_premium_entitlement_update(
    entitlement: discord.Entitlement,
    bot: commands.Bot | None = None
) -> None:
    if int(entitlement.sku_id) != settings.synto_premium_sku_id:
        return

    guild_id = _get_entitlement_guild_id(entitlement)

    if guild_id is None:
        return

    purchaser_user_id = _get_entitlement_user_id(entitlement)

    if _entitlement_is_active(entitlement):
        set_guild_premium_status(
            guild_id = guild_id,
            is_premium = True,
            entitlement_id = int(entitlement.id),
            sku_id = int(entitlement.sku_id),
            purchaser_user_id = purchaser_user_id,
            premium_ends_at = getattr(entitlement, 'ends_at', None)
        )

        print(f'✅ Premium active for guild_id={guild_id}')

        if bot is not None and purchaser_user_id is not None:
            from services.supporter_role import grant_supporter_role_if_missing

            await grant_supporter_role_if_missing(
                bot = bot,
                user_id = purchaser_user_id
            )

        return

    clear_guild_premium_status(
        guild_id = guild_id
    )

    print(f'🔒 Premium inactive for guild_id={guild_id}')


async def handle_premium_entitlement_delete(
    entitlement: discord.Entitlement
) -> None:
    if int(entitlement.sku_id) != settings.synto_premium_sku_id:
        return

    guild_id = _get_entitlement_guild_id(entitlement)

    if guild_id is None:
        return

    # An ENTITLEMENT_DELETE means the entitlement itself was removed
    # (refund/revocation) - this is distinct from a subscription simply
    # lapsing, which Discord instead reflects via ends_at on an update.
    # Access must be revoked immediately regardless of ends_at/deleted.
    clear_guild_premium_status(
        guild_id = guild_id
    )

    print(f'🔒 Premium revoked for guild_id={guild_id} (entitlement deleted)')



async def sync_premium_entitlements(bot: commands.Bot) -> None:
    print('🔄 Syncing premium entitlements...')

    from services.supporter_role import grant_supporter_role_if_missing

    active_premium_guild_ids: set[int] = set()

    try:
        async for entitlement in bot.entitlements(
            skus = [discord.Object(id = settings.synto_premium_sku_id)],
            exclude_ended = False,
            exclude_deleted = False
        ):
            guild_id = _get_entitlement_guild_id(entitlement)

            if guild_id is None:
                continue

            if not _entitlement_is_active(entitlement):
                continue

            active_premium_guild_ids.add(guild_id)
            purchaser_user_id = _get_entitlement_user_id(entitlement)

            set_guild_premium_status(
                guild_id = guild_id,
                is_premium = True,
                entitlement_id = int(entitlement.id),
                sku_id = int(entitlement.sku_id),
                purchaser_user_id = purchaser_user_id,
                premium_ends_at = getattr(entitlement, 'ends_at', None)
            )

            if purchaser_user_id is not None:
                await grant_supporter_role_if_missing(
                    bot = bot,
                    user_id = purchaser_user_id
                )

    except Exception as error:
        print(
            '❌ Failed to sync premium entitlements\n'
            f'{type(error).__name__}: {error}'
        )
        return

    cached_premium_guild_ids = get_cached_premium_guild_ids()

    expired_premium_guild_ids = (
        cached_premium_guild_ids
        - active_premium_guild_ids
    )

    set_many_guilds_not_premium(
        guild_ids = expired_premium_guild_ids
    )

    print(
        '✅ Premium entitlement sync complete | '
        f'active={len(active_premium_guild_ids)} '
        f'expired={len(expired_premium_guild_ids)}'
    )