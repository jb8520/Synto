from dataclasses import dataclass

@dataclass(slots = True)
class WelcomeMessageSettings:
    guild_id: int
    channel_id: int = 0
    title: str = 'Welcome!'
    description: str | None = None
    colour: str | None = None
    status: bool = False

    @property
    def is_configured(self) -> bool:
        return(
            self.channel_id != 0
            and self.status
        )
    
    @property
    def normalised_colour(self):
        if self.colour is None:
            return '000000'
        
        colour = self.colour.strip()

        if colour.startswith('#'):
            colour = colour[1:]
        
        return colour