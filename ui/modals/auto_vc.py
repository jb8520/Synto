import discord

from services.auto_vc import (
    rename_owned_auto_vc,
    set_owned_auto_vc_user_limit
)


class RenameModal(discord.ui.Modal, title = 'Rename Voice Channel'):
    name = discord.ui.TextInput(
        label = 'New voice channel name',
        placeholder = 'Enter the new name for your voice channel',
        style = discord.TextStyle.short,
        required = True,
        min_length = 1,
        max_length = 100
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ) -> None:
        _, message = await rename_owned_auto_vc(
            runtime = interaction.client.auto_vc_runtime,
            interaction = interaction,
            name = str(self.name)
        )

        await interaction.response.send_message(
            message,
            ephemeral = True
        )


class UserLimitModal(discord.ui.Modal, title = 'User Limit'):
    selected_limit = discord.ui.TextInput(
        label = 'User limit',
        placeholder = 'Enter 0 for no user limit',
        style = discord.TextStyle.short,
        required = True,
        min_length = 1,
        max_length = 2
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ) -> None:
        try:
            user_limit = int(str(self.selected_limit).strip())

        except ValueError:
            await interaction.response.send_message(
                '❌ The user limit must be a number between 0 and 99.',
                ephemeral = True
            )
            return

        _, message = await set_owned_auto_vc_user_limit(
            runtime = interaction.client.auto_vc_runtime,
            interaction = interaction,
            user_limit = user_limit
        )

        await interaction.response.send_message(
            message,
            ephemeral = True
        )