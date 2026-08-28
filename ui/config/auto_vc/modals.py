import discord

from database.repositories import (
    set_auto_vc_name,
    set_channel_name_template
)


class AutoVcNameModal(discord.ui.Modal, title = 'Auto VC Name'):
    name = discord.ui.TextInput(
        label = 'Auto VC name',
        placeholder = 'Example: Gaming, Study, Private VC',
        style = discord.TextStyle.short,
        required = True,
        min_length = 1,
        max_length = 50
    )

    def __init__(
        self,
        auto_vc_id: int
    ):
        super().__init__()

        self.auto_vc_id = auto_vc_id

    async def on_submit(
        self,
        interaction: discord.Interaction
    ) -> None:
        set_auto_vc_name(
            auto_vc_id = self.auto_vc_id,
            name = str(self.name).strip()
        )

        await interaction.response.send_message(
            '✅ Auto VC name updated.',
            ephemeral = True
        )


class ChannelNameTemplateModal(discord.ui.Modal, title = 'Channel Name Pattern'):
    channel_name_template = discord.ui.TextInput(
        label = 'Channel name pattern',
        placeholder = '{name} {number}',
        style = discord.TextStyle.short,
        required = True,
        min_length = 1,
        max_length = 100
    )

    def __init__(
        self,
        auto_vc_id: int
    ):
        super().__init__()

        self.auto_vc_id = auto_vc_id

    async def on_submit(
        self,
        interaction: discord.Interaction
    ) -> None:
        template = str(self.channel_name_template).strip()

        set_channel_name_template(
            auto_vc_id = self.auto_vc_id,
            channel_name_template = template
        )

        await interaction.response.send_message(
            '✅ Channel name pattern updated.',
            ephemeral = True
        )