import discord

from checks.permissions import admin_only_interaction

from database.models.auto_vc import AutoVCSettings
from database.repositories import (
    guild_has_premium_cached,
    count_auto_vc_settings,
    create_auto_vc_settings,
    delete_auto_vc_settings,
    get_auto_vc_settings,
    get_auto_vc_settings_for_guild,
    set_default_auto_vc
)

from services.auto_vc_limit import can_create_auto_vc_config

from ..common import BaseSettingsView

from .base_view import AutoVcMenuView
from .embed import build_auto_vc_embed
from .refresh_manager import refresh_auto_vc_manager_message

from ui.views.premium import PremiumUpsellView



class AutoVcManagerView(BaseSettingsView):
    information_title = 'Auto VC Manager Information ℹ️'

    information_fields = [
        (
            'Configure Auto VC',
            '> Select an Auto VC setup to configure its channels, roles, and naming.',
        ),
        (
            'Add Auto VC',
            '> Creates a new Auto VC setup for this server.',
        ),
        (
            'Delete Auto VC',
            '> Deletes an Auto VC setup. The default setup can only be deleted if it\'s the only setup remaining.',
        ),
        (
            'Change Default',
            '> Changes which Auto VC setup is treated as the default.',
        )
    ]

    def __init__(
        self,
        guild_id: int
    ):
        super().__init__(
            include_settings_menu = True,
            include_utility_buttons = True
        )

        self.guild_id = guild_id

        settings_list = get_auto_vc_settings_for_guild(
            guild_id = guild_id
        )

        if settings_list:
            self.add_item(
                AutoVcConfigSelect(
                    settings_list = settings_list
                )
            )

    @discord.ui.button(
        label = 'Add Auto VC',
        style = discord.ButtonStyle.grey,
        row = 1
    )
    async def add_auto_vc(
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

        can_create, message = can_create_auto_vc_config(interaction)

        if not can_create:
            await interaction.response.send_message(
                f'❌ {message}',
                ephemeral = True,
                view = PremiumUpsellView()
            )
            return

        is_first_setup = count_auto_vc_settings(interaction.guild.id) == 0

        auto_vc_id = create_auto_vc_settings(
            guild_id = interaction.guild.id,
            name = 'VC',
            is_default = is_first_setup
        )

        settings = get_auto_vc_settings(
            auto_vc_id = auto_vc_id
        )

        if settings is None:
            await interaction.response.send_message(
                '❌ Something went wrong creating the Auto VC setup.',
                ephemeral = True
            )
            return

        await interaction.response.send_message(
            embed = build_auto_vc_embed(
                guild = interaction.guild,
                settings = settings
            ),
            view = AutoVcMenuView(
                auto_vc_id = settings.id,
                include_settings_menu = False,
                include_utility_buttons = True,
                manager_message = interaction.message
            )
        )

        if interaction.message is None:
            return

        await refresh_auto_vc_manager_message(
            guild = interaction.guild,
            message = interaction.message
        )

    @discord.ui.button(
        label = 'Delete Auto VC',
        style = discord.ButtonStyle.grey,
        row = 1
    )
    async def delete_auto_vc(
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

        all_settings = get_auto_vc_settings_for_guild(interaction.guild.id)

        # The default can only be deleted when it's the sole remaining
        # setup - otherwise deleting it would leave the guild with other
        # setups but no default.
        if len(all_settings) == 1:
            settings_list = all_settings

        else:
            settings_list = [
                settings
                for settings in all_settings
                if not settings.is_default
            ]

        if not settings_list:
            await interaction.response.send_message(
                '❌ There are no Auto VC setups to delete.',
                ephemeral = True
            )
            return

        await interaction.response.send_message(
            'Select the Auto VC setup you want to delete.',
            view = DeleteAutoVcView(
                settings_list = settings_list,
                manager_message = interaction.message
            ),
            ephemeral = True
        )

    @discord.ui.button(
        label = 'Change Default',
        style = discord.ButtonStyle.grey,
        row = 1
    )
    async def change_default(
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

        settings_list = get_auto_vc_settings_for_guild(
            guild_id = interaction.guild.id
        )

        if len(settings_list) <= 1:
            await interaction.response.send_message(
                '❌ There is only one Auto VC setup.',
                ephemeral = True
            )
            return

        await interaction.response.send_message(
            'Select the Auto VC setup you want to make default.',
            view = ChangeDefaultAutoVcView(
                settings_list = settings_list,
                manager_message = interaction.message
            ),
            ephemeral = True
        )


class AutoVcConfigSelect(discord.ui.Select):
    def __init__(
        self,
        settings_list: list[AutoVCSettings]
    ):
        options = [
            discord.SelectOption(
                label = settings.name,
                value = str(settings.id),
                description = 'Default setup' if settings.is_default else 'Auto VC setup'
            )
            for settings in settings_list[:25]
        ]

        super().__init__(
            placeholder = 'Configure an Auto VC setup',
            min_values = 1,
            max_values = 1,
            options = options,
            row = 0
        )


    async def callback(
        self,
        interaction: discord.Interaction
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

        settings = get_auto_vc_settings(
            auto_vc_id = int(self.values[0])
        )

        if settings is None:
            await interaction.response.send_message(
                '❌ That Auto VC setup no longer exists.',
                ephemeral = True
            )
            return

        has_premium = guild_has_premium_cached(interaction.guild.id)

        if not has_premium and not settings.is_default:
            await interaction.response.send_message(
                content = (
                    '🔒 This Auto VC setup is locked because this server does not currently have Synto Premium.\n\n'
                    'You can make it the default setup, delete it, or renew Premium to edit and use multiple setups again.'
                ),
                view = PremiumUpsellView(),
                ephemeral = True
            )
            return
        
        await interaction.response.send_message(
            embed = build_auto_vc_embed(
                guild = interaction.guild,
                settings = settings
            ),
            view = AutoVcMenuView(
                auto_vc_id = settings.id,
                include_settings_menu = False,
                include_utility_buttons = True,
                manager_message = interaction.message
            )
        )

        if interaction.message is None:
            return

        await refresh_auto_vc_manager_message(
            guild = interaction.guild,
            message = interaction.message
        )


class DeleteAutoVcView(discord.ui.View):
    def __init__(
        self,
        settings_list: list[AutoVCSettings],
        manager_message: discord.Message | None
    ):
        super().__init__(timeout = 120)

        self.manager_message = manager_message

        self.add_item(
            DeleteAutoVcSelect(
                settings_list = settings_list,
                manager_message = manager_message
            )
        )


class DeleteAutoVcSelect(discord.ui.Select):
    def __init__(
        self,
        settings_list: list[AutoVCSettings],
        manager_message: discord.Message | None
    ):
        options = [
            discord.SelectOption(
                label = settings.name,
                value = str(settings.id),
                description = 'Delete this Auto VC setup'
            )
            for settings in settings_list[:25]
        ]

        super().__init__(
            placeholder = 'Select an Auto VC setup to delete',
            min_values = 1,
            max_values = 1,
            options = options
        )

        self.manager_message = manager_message

    async def callback(
        self,
        interaction: discord.Interaction
    ) -> None:
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        if interaction.guild is None:
            await interaction.response.edit_message(
                content = '❌ This can only be used in a server.',
                view = None
            )
            return

        success, message = delete_auto_vc_settings(
            auto_vc_id = int(self.values[0])
        )

        emoji = '✅' if success else '❌'

        await interaction.response.edit_message(
            content = f'{emoji} {message}',
            view = None
        )

        if self.manager_message is None:
            return

        await refresh_auto_vc_manager_message(
            guild = interaction.guild,
            message = self.manager_message
        )


class ChangeDefaultAutoVcView(discord.ui.View):
    def __init__(
        self,
        settings_list: list[AutoVCSettings],
        manager_message: discord.Message | None
    ):
        super().__init__(timeout = 120)

        self.manager_message = manager_message

        self.add_item(
            ChangeDefaultAutoVcSelect(
                settings_list = settings_list,
                manager_message = manager_message
            )
        )


class ChangeDefaultAutoVcSelect(discord.ui.Select):
    def __init__(
        self,
        settings_list: list[AutoVCSettings],
        manager_message: discord.Message | None
    ):
        options = [
            discord.SelectOption(
                label = settings.name,
                value = str(settings.id),
                description = 'Current default' if settings.is_default else 'Make this the default'
            )
            for settings in settings_list[:25]
        ]

        super().__init__(
            placeholder = 'Select the new default Auto VC setup',
            min_values = 1,
            max_values = 1,
            options = options
        )

        self.manager_message = manager_message

    async def callback(
        self,
        interaction: discord.Interaction
    ) -> None:
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        if interaction.guild is None:
            await interaction.response.edit_message(
                content = '❌ This can only be used in a server.',
                view = None
            )
            return

        success = set_default_auto_vc(
            auto_vc_id = int(self.values[0])
        )

        if not success:
            await interaction.response.edit_message(
                content = '❌ That Auto VC setup no longer exists.',
                view = None
            )
            return

        await interaction.response.edit_message(
            content = '✅ Default Auto VC setup updated.',
            view = None
        )

        if self.manager_message is None:
            return

        await refresh_auto_vc_manager_message(
            guild = interaction.guild,
            message = self.manager_message
        )
