from discord import Interaction

from database.repositories import (
    count_auto_vc_settings,
    guild_has_premium_cached
)


FREE_AUTO_VC_LIMIT = 1
PREMIUM_AUTO_VC_LIMIT = 5


def get_auto_vc_config_limit(interaction: Interaction) -> int:
    if interaction.guild_id is None:
        return FREE_AUTO_VC_LIMIT

    return (
        PREMIUM_AUTO_VC_LIMIT
        if guild_has_premium_cached(interaction.guild_id)
        else FREE_AUTO_VC_LIMIT
    )


def can_create_auto_vc_config(interaction: Interaction) -> tuple[bool, str]:
    if interaction.guild_id is None:
        return False, 'This can only be used in a server.'

    current_count = count_auto_vc_settings(interaction.guild_id)
    limit = get_auto_vc_config_limit(interaction)

    if current_count >= limit:
        if limit == FREE_AUTO_VC_LIMIT:
            message = (
                'Free servers can only create 1 Auto VC setup. '
                'Synto Premium unlocks up to 5 setups for this server.'
            )
        
        else:
            setup_word = 'setup' if limit == 1 else 'setups'
            message = f'You can only have {limit} Auto VC {setup_word}.'
        
        return False, message

    return True, ''