from dataclasses import dataclass, field

@dataclass(slots = True)
class AutoVCSettings:
    id: int
    guild_id: int
    name: str = 'VC'

    vc_creator_id: int | None = None
    vc_category_id: int | None = None
    member_role_id: int | None = None

    moderator_role_ids: list[int] = field(default_factory = list)

    is_enabled: bool = True
    is_default: bool = False

    position: int = 0
    channel_name_template: str = '{name} {number}'

    @property
    def is_configured(self) -> bool:
        return (
            self.vc_creator_id is not None
            and self.vc_category_id is not None
            and self.member_role_id is not None
        )