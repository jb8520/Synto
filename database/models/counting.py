from dataclasses import dataclass

@dataclass(slots = True)
class CountingSettings:
    guild_id: int
    channel_id: int = 0
    highscore: int = 0
    current_score: int = 0
    last_message_id: int = 0
    last_author_id: int = 0
    double_count: bool = False
    counting_saves_enabled: bool = True

    @property
    def is_configured(self) -> bool:
        return self.channel_id != 0