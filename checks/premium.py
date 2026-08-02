import discord

from settings import settings


def guild_has_premium(interaction: discord.Interaction) -> bool:
    if interaction.guild_id is None:
        return False

    return any(
        entitlement.sku_id == settings.synto_premium_sku_id
        and getattr(entitlement, 'guild_id', None) == interaction.guild_id
        for entitlement in interaction.entitlements
    )