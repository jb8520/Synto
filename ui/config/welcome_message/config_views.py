import discord

from checks.permissions import admin_only_interaction

from database.repositories import set_welcome_channel

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