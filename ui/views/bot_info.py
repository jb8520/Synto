import discord


BUY_ME_A_COFFEE_URL = 'https://buymeacoffee.com/synto'


class BuyMeACoffeeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)

        self.add_item(
            discord.ui.Button(
                label = 'Buy Me a Coffee',
                style = discord.ButtonStyle.link,
                url = BUY_ME_A_COFFEE_URL,
                emoji = '☕'
            )
        )
