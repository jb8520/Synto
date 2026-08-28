from dataclasses import dataclass, field


@dataclass(slots = True)
class PendingCountBreak:
    guild_id: int
    breaking_user_id: int
    broken_at_score: int
    reason: str | None


@dataclass(slots = True)
class CountingSaveRuntime:
    pending_breaks: dict[int, PendingCountBreak] = field(default_factory = dict)

    def get_pending_break(self, guild_id: int) -> PendingCountBreak | None:
        return self.pending_breaks.get(guild_id)

    def start_pending_break(
        self,
        guild_id: int,
        breaking_user_id: int,
        broken_at_score: int,
        reason: str | None
    ) -> PendingCountBreak | None:
        if guild_id in self.pending_breaks:
            return None

        pending = PendingCountBreak(
            guild_id = guild_id,
            breaking_user_id = breaking_user_id,
            broken_at_score = broken_at_score,
            reason = reason
        )

        self.pending_breaks[guild_id] = pending

        return pending

    def clear_pending_break(self, guild_id: int) -> None:
        self.pending_breaks.pop(guild_id, None)
