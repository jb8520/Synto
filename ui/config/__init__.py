from database.repositories import get_general_settings, guild_has_premium_cached


SETTINGS_COLOUR = 0x00F3FF


def get_settings_colour(guild_id: int) -> int:
    if not guild_has_premium_cached(guild_id):
        return SETTINGS_COLOUR

    general_settings = get_general_settings(guild_id)

    if general_settings.normalised_colour is None:
        return SETTINGS_COLOUR

    try:
        return int(general_settings.normalised_colour, 16)

    except ValueError:
        return SETTINGS_COLOUR
