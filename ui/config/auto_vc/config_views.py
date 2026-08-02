import discord

from checks.permissions import admin_only_interaction

from database.repositories import (
    set_vc_creator,
    set_vc_category,
    set_member_role,
    set_moderator_roles
)

from .. import SETTINGS_COLOUR


class AutoVcCreatorView(discord.ui.View):
    def __init__(
        self,
        auto_vc_id: int
    ):
        super().__init__(timeout = None)
        self.add_item(
            AutoVcCreatorSelect(
                parent_view = self,
                auto_vc_id = auto_vc_id
            )
        )

class AutoVcCreatorSelect(discord.ui.ChannelSelect):
    def __init__(
        self,
        parent_view: AutoVcCreatorView,
        auto_vc_id: int
    ):
        super().__init__(
            placeholder = 'VC Creator Channel',
            min_values = 1,
            max_values = 1,
            channel_types = [discord.ChannelType.voice]
        )

        self.parent_view = parent_view
        self.auto_vc_id = auto_vc_id

    async def callback(self, interaction: discord.Interaction):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return
        
        await interaction.response.defer()

        selected_channel = self.values[0]

        set_vc_creator(
            auto_vc_id = self.auto_vc_id,
            vc_creator_id = selected_channel.id
        )

        await interaction.edit_original_response(
            embed = discord.Embed(
                description = f'Successfully set the VC creator channel to {selected_channel.mention}.',
                colour = SETTINGS_COLOUR
            ),
            view = None
        )

        self.parent_view.stop()


class AutoVcCategoryView(discord.ui.View):
    def __init__(
        self,
        auto_vc_id: int
    ):
        super().__init__(timeout = None)
        self.add_item(
            AutoVcCategorySelect(
                parent_view = self,
                auto_vc_id = auto_vc_id
            )
        )

class AutoVcCategorySelect(discord.ui.ChannelSelect):
    def __init__(
        self,
        parent_view: AutoVcCategoryView,
        auto_vc_id: int
    ):
        super().__init__(
            placeholder = 'VC Category',
            min_values = 1,
            max_values = 1,
            channel_types = [discord.ChannelType.category],
        )

        self.parent_view = parent_view
        self.auto_vc_id = auto_vc_id

    async def callback(self, interaction: discord.Interaction):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return
        
        await interaction.response.defer()

        selected_category = self.values[0]

        set_vc_category(
            auto_vc_id = self.auto_vc_id,
            vc_category_id = selected_category.id
        )

        await interaction.edit_original_response(
            embed = discord.Embed(
                description = f'Successfully set the VC category to `{selected_category.name}`.',
                colour = SETTINGS_COLOUR
            ),
            view = None
        )

        self.parent_view.stop()


class MemberRoleView(discord.ui.View):
    def __init__(
        self,
        auto_vc_id: int
    ):
        super().__init__(timeout = None)
        self.add_item(
            MemberRoleSelect(
                parent_view = self,
                auto_vc_id = auto_vc_id
            )
        )


class MemberRoleSelect(discord.ui.RoleSelect):
    def __init__(
        self,
        parent_view: MemberRoleView,
        auto_vc_id: int
    ):
        super().__init__(
            placeholder = 'Member Role',
            min_values = 1,
            max_values = 1
        )

        self.parent_view = parent_view
        self.auto_vc_id = auto_vc_id

    async def callback(self, interaction: discord.Interaction):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return
        
        await interaction.response.defer()

        selected_role = self.values[0]

        set_member_role(
            auto_vc_id = self.auto_vc_id,
            member_role_id = selected_role.id,
        )

        await interaction.edit_original_response(
            embed = discord.Embed(
                description = f'Successfully set the member role to {selected_role.mention}.',
                colour = SETTINGS_COLOUR
            ),
            view = None
        )

        self.parent_view.stop()


class ModeratorRolesView(discord.ui.View):
    def __init__(
        self,
        auto_vc_id: int
    ):
        super().__init__(timeout = None)
        self.add_item(
            ModeratorRolesSelect(
                parent_view = self,
                auto_vc_id = auto_vc_id
            )
        )

class ModeratorRolesSelect(discord.ui.RoleSelect):
    def __init__(
        self,
        parent_view: ModeratorRolesView,
        auto_vc_id: int
    ):
        super().__init__(
            placeholder = 'Moderator Roles',
            min_values = 0,
            max_values = 10
        )

        self.parent_view = parent_view
        self.auto_vc_id = auto_vc_id

    async def callback(self, interaction: discord.Interaction):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return
        
        await interaction.response.defer()

        selected_roles = self.values
        
        selected_role_ids = [role.id for role in selected_roles]

        set_moderator_roles(
            auto_vc_id = self.auto_vc_id,
            role_ids = selected_role_ids
        )

        if len(selected_roles) == 0:
            description = 'Auto VC moderator roles have been cleared.'
        
        else:
            role_mentions = ', '.join(role.mention for role in selected_roles)
            
            description = f'Successfully set Auto VC moderator roles to {role_mentions}.'

        await interaction.edit_original_response(
            embed = discord.Embed(
                description = description,
                colour = SETTINGS_COLOUR
            ),
            view = None
        )

        self.parent_view.stop()