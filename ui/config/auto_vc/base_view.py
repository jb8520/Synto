import discord

from checks.permissions import admin_only_interaction

from database.repositories import (
    get_auto_vc_settings,
    toggle_auto_vc_enabled
)

from ..common import BaseSettingsView

from .. import SETTINGS_COLOUR

from .embed import build_auto_vc_embed

from .refresh_manager import refresh_auto_vc_manager_message

from .modals import (
    AutoVcNameModal,
    ChannelNameTemplateModal
)

from .config_views import (
    AutoVcCreatorView,
    AutoVcCategoryView,
    MemberRoleView,
    ModeratorRolesView
)


class AutoVcMenuView(BaseSettingsView):
    information_title = 'Auto VC Settings Information ℹ️'
    information_fields = [
        (
            'VC Creator Channel',
            '> The voice channel members join to automatically create their own temporary voice channel.',
        ),
        (
            'VC Category',
            '> The category where temporary voice channels will be created.',
        ),
        (
            'Member Role',
            '> The role required to create and manage an Auto VC.',
        ),
        (
            'Moderator Roles',
            '> Roles that can bypass normal Auto VC ownership restrictions.',
        ),
        (
            'Name',
            '> The display name for this Auto VC setup, used by the `{name}` placeholder in the naming pattern.',
        ),
        (
            'Naming Pattern',
            '> The template used to name created voice channels. Supports `{name}`, `{number}`, `{member_name}`, `{username}`, and `{server}`.',
        ),
        (
            'Status',
            '> Whether this Auto VC setup is active. Disabled setups will not create voice channels when their VC Creator channel is joined. '
            'Non-default setups also require Synto Premium - `Locked (Premium required)` means the setup is enabled but this server no longer has Premium.',
        ),
    ]


    def __init__(
        self,
        auto_vc_id: int,
        include_settings_menu: bool = True,
        include_utility_buttons: bool = True,
        manager_message: discord.Message | None = None
    ):
        super().__init__(
            include_settings_menu = include_settings_menu,
            include_utility_buttons = include_utility_buttons
        )

        self.auto_vc_id = auto_vc_id
        self.manager_message = manager_message
    

    information_title = 'Auto VC Settings Information ℹ️'


    @discord.ui.button(
        label = 'VC Creator',
        style = discord.ButtonStyle.grey,
        row = 0
    )
    async def vc_creator(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return
        
        await interaction.response.defer(
            ephemeral = True,
            thinking = True
        )

        settings = get_auto_vc_settings(auto_vc_id = self.auto_vc_id)

        if settings.vc_creator_id == 0:
            channel = '`Not set`'
        
        else:
            discord_channel = interaction.guild.get_channel(settings.vc_creator_id)
            
            channel = (
                discord_channel.mention
                if discord_channel is not None
                else '`Unknown channel`'
            )

        view = AutoVcCreatorView(auto_vc_id = self.auto_vc_id)

        await interaction.followup.send(
            embed = discord.Embed(
                description = f'The VC creator channel is currently set to {channel}.',
                colour = SETTINGS_COLOUR
            ),
            view = view,
            ephemeral = True
        )

        await view.wait()

        settings = get_auto_vc_settings(auto_vc_id = self.auto_vc_id)

        await interaction.message.edit(
            embed = build_auto_vc_embed(
                guild = interaction.guild,
                settings = settings
            )
        )

        if self.manager_message is None:
            return
        
        await refresh_auto_vc_manager_message(
            guild = interaction.guild,
            message = self.manager_message
        )


    @discord.ui.button(
        label = 'VC Category',
        style = discord.ButtonStyle.grey,
        row = 0
    )
    async def vc_category(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return
        
        await interaction.response.defer(
            ephemeral = True,
            thinking = True
        )

        settings = get_auto_vc_settings(auto_vc_id = self.auto_vc_id)

        if settings.vc_category_id == 0:
            category = '`Not set`'
        
        else:
            discord_category = interaction.guild.get_channel(settings.vc_category_id)
            
            category = (
                discord_category.name
                if discord_category is not None
                else '`Unknown category`'
            )

        view = AutoVcCategoryView(auto_vc_id = self.auto_vc_id)

        await interaction.followup.send(
            embed = discord.Embed(
                description = f'The VC category is currently set to {category}.',
                colour = SETTINGS_COLOUR
            ),
            view = view,
            ephemeral = True
        )

        await view.wait()

        settings = get_auto_vc_settings(auto_vc_id = self.auto_vc_id)

        await interaction.message.edit(
            embed = build_auto_vc_embed(
                guild = interaction.guild,
                settings = settings
            )
        )

        if self.manager_message is None:
            return
        
        await refresh_auto_vc_manager_message(
            guild = interaction.guild,
            message = self.manager_message
        )


    @discord.ui.button(
        label = 'Member Role',
        style = discord.ButtonStyle.grey,
        row = 1
    )
    async def member_role(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return
        
        await interaction.response.defer(
            ephemeral = True,
            thinking = True
        )

        settings = get_auto_vc_settings(auto_vc_id = self.auto_vc_id)

        if settings.member_role_id == 0:
            role = '`Not set`'
        
        else:
            discord_role = interaction.guild.get_role(settings.member_role_id)
            
            role = discord_role.mention if discord_role is not None else '`Unknown role`'

        view = MemberRoleView(auto_vc_id = self.auto_vc_id)

        await interaction.followup.send(
            embed = discord.Embed(
                description = f'The member role is currently set to {role}.',
                colour = SETTINGS_COLOUR
            ),
            view = view,
            ephemeral = True
        )

        await view.wait()

        settings = get_auto_vc_settings(auto_vc_id = self.auto_vc_id)

        await interaction.message.edit(
            embed = build_auto_vc_embed(
                guild = interaction.guild,
                settings = settings
            )
        )

        if self.manager_message is None:
            return
        
        await refresh_auto_vc_manager_message(
            guild = interaction.guild,
            message = self.manager_message
        )


    @discord.ui.button(
        label = 'Moderator Roles',
        style = discord.ButtonStyle.grey,
        row = 1
    )
    async def moderator_roles(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return
        
        await interaction.response.defer(
            ephemeral = True,
            thinking = True
        )

        view = ModeratorRolesView(auto_vc_id = self.auto_vc_id)

        await interaction.followup.send(
            embed = discord.Embed(
                description = 'Select the Auto VC moderator roles.',
                colour = SETTINGS_COLOUR
            ),
            view = view,
            ephemeral = True
        )

        await view.wait()

        settings = get_auto_vc_settings(auto_vc_id = self.auto_vc_id)

        await interaction.message.edit(
            embed = build_auto_vc_embed(
                guild = interaction.guild,
                settings = settings
            )
        )

        if self.manager_message is None:
            return
        
        await refresh_auto_vc_manager_message(
            guild = interaction.guild,
            message = self.manager_message
        )
    

    @discord.ui.button(
        label = 'Name',
        style = discord.ButtonStyle.grey,
        row = 2
    )
    async def name(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ) -> None:
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        name_modal = AutoVcNameModal(auto_vc_id = self.auto_vc_id)

        await interaction.response.send_modal(name_modal)

        await name_modal.wait()

        settings = get_auto_vc_settings(auto_vc_id = self.auto_vc_id)

        await interaction.message.edit(
            embed = build_auto_vc_embed(
                guild = interaction.guild,
                settings = settings
            )
        )

        if self.manager_message is None:
            return
        
        await refresh_auto_vc_manager_message(
            guild = interaction.guild,
            message = self.manager_message
        )


    @discord.ui.button(
        label = 'Naming Pattern',
        style = discord.ButtonStyle.grey,
        row = 2
    )
    async def naming_pattern(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ) -> None:
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        naming_pattern_modal = ChannelNameTemplateModal(auto_vc_id = self.auto_vc_id)

        await interaction.response.send_modal(naming_pattern_modal)

        await naming_pattern_modal.wait()

        settings = get_auto_vc_settings(auto_vc_id = self.auto_vc_id)

        await interaction.message.edit(
            embed = build_auto_vc_embed(
                guild = interaction.guild,
                settings = settings
            )
        )

        if self.manager_message is None:
            return
        
        await refresh_auto_vc_manager_message(
            guild = interaction.guild,
            message = self.manager_message
        )
    

    @discord.ui.button(
        label = 'Enabled',
        style = discord.ButtonStyle.grey,
        row = 2
    )
    async def enabled(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ) -> None:
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        if interaction.guild is None:
            await interaction.response.send_message(
                '❌ This can only be used in a server.',
                ephemeral = True
            )
            return

        new_enabled = toggle_auto_vc_enabled(
            auto_vc_id = self.auto_vc_id
        )

        if new_enabled is None:
            await interaction.response.send_message(
                '❌ That Auto VC setup no longer exists.',
                ephemeral = True
            )
            return

        settings = get_auto_vc_settings(
            auto_vc_id = self.auto_vc_id
        )

        if settings is None:
            await interaction.response.send_message(
                '❌ That Auto VC setup no longer exists.',
                ephemeral = True
            )
            return

        message = (
            '✅ Auto VC setup enabled.'
            if new_enabled
            else '✅ Auto VC setup disabled.'
        )

        await interaction.response.edit_message(
            embed = build_auto_vc_embed(
                guild = interaction.guild,
                settings = settings
            )
        )

        await interaction.followup.send(
            message,
            ephemeral = True
        )

        if self.manager_message is None:
                return
            
        await refresh_auto_vc_manager_message(
            guild = interaction.guild,
            message = self.manager_message
        )