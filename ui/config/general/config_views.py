import discord

from checks.permissions import admin_only_interaction

from database.repositories import (
    set_updates_channel,
    set_general_admin_roles
)

from .. import get_settings_colour


class UpdatesChannelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)
        self.add_item(UpdatesChannelSelect(self))


class UpdatesChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, parent_view: UpdatesChannelView):
        super().__init__(
            placeholder = 'Updates Channel',
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

        set_updates_channel(
            guild_id = interaction.guild.id,
            channel_id = selected_channel.id
        )

        await interaction.edit_original_response(
            embed = discord.Embed(
                description = (
                    f'Successfully set the updates channel to '
                    f'{selected_channel.mention}.'
                ),
                colour = get_settings_colour(interaction.guild.id)
            ),
            view = None
        )

        self.parent_view.stop()


class AdminRolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)
        self.add_item(AdminRolesSelect(self))


class AdminRolesSelect(discord.ui.RoleSelect):
    def __init__(self, parent_view: AdminRolesView):
        super().__init__(
            placeholder = 'Admin Roles',
            min_values = 0,
            max_values = 10
        )

        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        await interaction.response.defer()

        selected_roles = self.values
        role_ids = [role.id for role in selected_roles]

        set_general_admin_roles(
            guild_id = interaction.guild.id,
            role_ids = role_ids
        )

        if not selected_roles:
            description = 'Admin roles have been cleared.'

        else:
            role_mentions = ', '.join(role.mention for role in selected_roles)
            description = f'Successfully set admin roles to {role_mentions}.'

        await interaction.edit_original_response(
            embed = discord.Embed(
                description = description,
                colour = get_settings_colour(interaction.guild.id)
            ),
            view = None
        )

        self.parent_view.stop()
