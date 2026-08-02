import discord

from settings import settings


class PremiumUpsellView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)

        self.add_item(
            discord.ui.Button(
                style = discord.ButtonStyle.premium,
                sku_id = settings.synto_premium_sku_id
            )
        )


class CountingSavesUpsellView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)

        self.add_item(
            discord.ui.Button(
                style = discord.ButtonStyle.premium,
                sku_id = settings.counting_save_1_sku_id
            )
        )

        self.add_item(
            discord.ui.Button(
                style = discord.ButtonStyle.premium,
                sku_id = settings.counting_save_3_sku_id
            )
        )

        self.add_item(
            discord.ui.Button(
                style = discord.ButtonStyle.premium,
                sku_id = settings.counting_save_10_sku_id
            )
        )