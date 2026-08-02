from dataclasses import dataclass

from datetime import datetime

from typing import Any

@dataclass(slots = True)
class Metrics:
    id: int
    user_id: int
    guild_id: int
    timestamp: datetime
    action_type: str
    command_name: str | None = None
    auto_vc_type: str | None = None
    details: dict[str, Any] | None = None