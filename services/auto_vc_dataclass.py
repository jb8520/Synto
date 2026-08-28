from dataclasses import dataclass, field


@dataclass(slots = True)
class TempAutoVc:
    generator_id: int
    channel_id: int
    owner_id: int | None
    number: int


@dataclass(slots = True)
class AutoVcRuntime:
    temp_channels: dict[int, dict[int, list[TempAutoVc]]] = field(default_factory = dict)

    def get_guild_generators(self, guild_id: int) -> dict[int, list[TempAutoVc]]:
        return self.temp_channels.setdefault(guild_id, {})

    def get_generator_channels(
        self,
        guild_id: int,
        generator_id: int
    ) -> list[TempAutoVc]:
        guild_generators = self.get_guild_generators(guild_id)

        return guild_generators.setdefault(generator_id, [])

    def add_channel(
        self,
        guild_id: int,
        generator_id: int,
        channel_id: int,
        owner_id: int,
        number: int
    ) -> None:
        self.get_generator_channels(
            guild_id = guild_id,
            generator_id = generator_id
        ).append(
            TempAutoVc(
                channel_id = channel_id,
                owner_id = owner_id,
                number = number,
                generator_id = generator_id
            )
        )

    def remove_channel(
        self,
        guild_id: int,
        generator_id: int,
        channel_id: int
    ) -> None:
        generator_channels = self.get_generator_channels(
            guild_id = guild_id,
            generator_id = generator_id
        )

        generator_channels[:] = [
            temp_vc
            for temp_vc in generator_channels
            if temp_vc.channel_id != channel_id
        ]

        if generator_channels:
            return

        guild_generators = self.get_guild_generators(guild_id)

        guild_generators.pop(generator_id, None)

        if not guild_generators:
            self.temp_channels.pop(guild_id, None)

    def find_by_channel(
        self,
        guild_id: int,
        channel_id: int
    ) -> TempAutoVc | None:
        guild_generators = self.get_guild_generators(guild_id)

        for generator_channels in guild_generators.values():
            for temp_vc in generator_channels:
                if temp_vc.channel_id == channel_id:
                    return temp_vc

        return None

    def find_by_owner(
        self,
        guild_id: int,
        owner_id: int
    ) -> TempAutoVc | None:
        guild_generators = self.get_guild_generators(guild_id)

        for generator_channels in guild_generators.values():
            for temp_vc in generator_channels:
                if temp_vc.owner_id == owner_id:
                    return temp_vc

        return None

    def find_user_current_channel(
        self,
        guild_id: int,
        user_id: int
    ) -> TempAutoVc | None:
        return self.find_by_owner(
            guild_id = guild_id,
            owner_id = user_id
        )

    def clear_owner(
        self,
        guild_id: int,
        owner_id: int
    ) -> None:
        temp_vc = self.find_by_owner(
            guild_id = guild_id,
            owner_id = owner_id
        )

        if temp_vc is not None:
            temp_vc.owner_id = None

    def next_number(
        self,
        guild_id: int,
        generator_id: int
    ) -> int:
        used_numbers = {
            temp_vc.number
            for temp_vc in self.get_generator_channels(
                guild_id = guild_id,
                generator_id = generator_id
            )
        }

        number = 1

        while number in used_numbers:
            number += 1

        return number