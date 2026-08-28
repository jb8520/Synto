from dataclasses import dataclass, field


@dataclass(slots = True)
class GeneralSettings:
    guild_id: int

    auto_vc_enabled: bool = True
    counting_enabled: bool = True
    games_enabled: bool = True

    embed_colour: str | None = None

    updates_channel_id: int = 0

    admin_role_ids: list[int] = field(default_factory = list)

    @property
    def normalised_colour(self) -> str | None:
        if self.embed_colour is None:
            return None

        colour = self.embed_colour.strip()

        if colour.startswith('#'):
            colour = colour[1:]

        return colour
