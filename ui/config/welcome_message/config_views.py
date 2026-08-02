import discord

from checks.permissions import admin_only_interaction

from database.repositories import (
    set_welcome_channel,
    set_welcome_status
)

from .. import SETTINGS_COLOUR


class WelcomeChannelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)
        self.add_item(WelcomeChannelSelect(self))

class WelcomeChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, parent_view: WelcomeChannelView):
        super().__init__(
            placeholder = 'Welcome Channel',
            min_values = 1,
            max_values = 1,
            channel_types = [discord.ChannelType.text]
        )

        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return
        
        await interaction.response.defer()

        selected_channel = self.values[0]

        set_welcome_channel(
            guild_id = interaction.guild.id,
            channel_id = selected_channel.id
        )

        await interaction.edit_original_response(
            embed = discord.Embed(
                description = (
                    f'Successfully set the welcome channel to '
                    f'{selected_channel.mention}.'
                ),
                colour = SETTINGS_COLOUR
            ),
            view = None
        )

        self.parent_view.stop()


class WelcomeStatusView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)


    async def _set_status(
        self,
        interaction: discord.Interaction,
        status: bool
    ) -> None:
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        await interaction.response.defer()

        set_welcome_status(
            guild_id = interaction.guild.id,
            status = status
        )

        await interaction.edit_original_response(
            embed = discord.Embed(
                description = f'Welcome messages have been set to `{status}`.',
                colour = SETTINGS_COLOUR
            ),
            view = None
        )

        self.stop()
    

    @discord.ui.button(
        emoji = '✅',
        label = 'True',
        style = discord.ButtonStyle.grey
    )
    async def true(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ):
        await self._set_status(
            interaction = interaction,
            status = True
        )  

    @discord.ui.button(
        emoji = '❌',
        label = 'False',
        style = discord.ButtonStyle.grey
    )
    async def false(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ):
        await self._set_status(
            interaction = interaction,
            status = False
        )