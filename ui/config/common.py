import discord

from checks.permissions import admin_only_interaction

from .main_menu import ConfigMenuView

from . import SETTINGS_COLOUR



class InformationButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            emoji = 'ℹ️',
            style = discord.ButtonStyle.blurple,
            row = 3
        )

    async def callback(self, interaction: discord.Interaction):
        view: BaseSettingsView = self.view  # type: ignore

        await interaction.response.send_message(
            embed = view.build_information_embed(),
            ephemeral = True
        )


class DeleteButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            emoji = '🗑️',
            style = discord.ButtonStyle.red,
            row = 3
        )

    async def callback(self, interaction: discord.Interaction):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        await interaction.response.defer()
        await interaction.message.delete()


class BaseSettingsView(ConfigMenuView):
    information_title: str = 'Settings Information ℹ️'
    information_fields: list[tuple[str, str]] = []

    def __init__(
        self,
        include_settings_menu: bool = True,
        include_utility_buttons: bool = True
    ):
        if include_settings_menu:
            super().__init__(timeout = None)

        else:
            discord.ui.View.__init__(
                self,
                timeout = None
            )

        if include_utility_buttons:
            self.add_item(
                InformationButton()
            )

            self.add_item(
                DeleteButton()
            )

    def build_information_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title = self.information_title,
            colour = SETTINGS_COLOUR,
        )

        for name, value in self.information_fields:
            embed.add_field(
                name = name,
                value = value,
                inline = False,
            )

        return embed