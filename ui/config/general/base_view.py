import discord

from checks.permissions import admin_only_interaction

from database.repositories import (
    get_general_settings,
    guild_has_premium_cached,
    toggle_auto_vc_module_enabled,
    toggle_counting_module_enabled,
    toggle_games_module_enabled,
    toggle_welcome_status
)

from ..common import BaseSettingsView
from .. import get_settings_colour

from .embed import build_general_embed

from .config_views import (
    AdminRolesView,
    UpdatesChannelView
)

from .config_modals import GeneralEmbedColourModal

from ui.views.premium import PremiumUpsellView


class GeneralMenuView(BaseSettingsView):
    information_title = 'General Settings Information ℹ️'

    information_fields = [
        (
            'Admin Roles',
            '> Roles that can use Synto\'s admin-only features, in addition to '
            'members with the Administrator permission.'
        ),
        (
            'Embed Colour',
            '> Premium feature - customises the accent colour used across Synto\'s '
            'settings and info embeds for this server.'
        ),
        (
            'Updates Channel',
            '> The channel where Synto posts announcements about new features and fixes.'
        ),
        (
            'Auto VC',
            '> Whether Auto VC is enabled for this server.'
        ),
        (
            'Counting',
            '> Whether the counting game is enabled for this server.'
        ),
        (
            'Games',
            '> Whether TicTacToe, Connect 4, and Rock Paper Scissors are enabled for this server.'
        ),
        (
            'Welcome Message',
            '> Whether welcome messages are enabled - the same toggle as the '
            'Welcome Message section\'s Status button.'
        ),
    ]

    @discord.ui.button(
        label = 'Admin Roles',
        style = discord.ButtonStyle.grey,
        row = 0
    )
    async def admin_roles(
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

        settings = get_general_settings(interaction.guild.id)

        if settings.admin_role_ids:
            roles_text = ', '.join(f'<@&{role_id}>' for role_id in settings.admin_role_ids)

        else:
            roles_text = '`None set`'

        view = AdminRolesView()

        await interaction.followup.send(
            embed = discord.Embed(
                description = f'Admin roles are currently set to {roles_text}.',
                colour = get_settings_colour(interaction.guild.id)
            ),
            view = view,
            ephemeral = True
        )

        await view.wait()

        await interaction.message.edit(
            embed = build_general_embed(interaction),
            view = GeneralMenuView()
        )

    @discord.ui.button(
        label = 'Embed Colour',
        style = discord.ButtonStyle.grey,
        row = 0
    )
    async def embed_colour(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        if not guild_has_premium_cached(interaction.guild.id):
            await interaction.response.send_message(
                '🔒 Custom embed colours are a Synto Premium feature.',
                view = PremiumUpsellView(),
                ephemeral = True
            )
            return

        colour_modal = GeneralEmbedColourModal()

        await interaction.response.send_modal(colour_modal)

        await colour_modal.wait()

        await interaction.message.edit(
            embed = build_general_embed(interaction),
            view = GeneralMenuView()
        )

    @discord.ui.button(
        label = 'Updates Channel',
        style = discord.ButtonStyle.grey,
        row = 0
    )
    async def updates_channel(
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

        settings = get_general_settings(interaction.guild.id)

        if settings.updates_channel_id == 0:
            channel = '`Not set`'

        else:
            discord_channel = interaction.guild.get_channel(settings.updates_channel_id)
            channel = (
                discord_channel.mention
                if discord_channel is not None
                else '`Unknown channel`'
            )

        view = UpdatesChannelView()

        await interaction.followup.send(
            embed = discord.Embed(
                description = f'The updates channel is currently set to {channel}.',
                colour = get_settings_colour(interaction.guild.id)
            ),
            view = view,
            ephemeral = True
        )

        await view.wait()

        await interaction.message.edit(
            embed = build_general_embed(interaction),
            view = GeneralMenuView()
        )

    async def _toggle(
        self,
        interaction: discord.Interaction,
        toggler,
        label: str
    ) -> None:
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        new_value = toggler(interaction.guild.id)

        await interaction.response.edit_message(
            embed = build_general_embed(interaction),
            view = GeneralMenuView()
        )

        await interaction.followup.send(
            embed = discord.Embed(
                description = f'{label} has been set to `{new_value}`.',
                colour = get_settings_colour(interaction.guild.id)
            ),
            ephemeral = True
        )

    @discord.ui.button(
        label = 'Auto VC',
        style = discord.ButtonStyle.grey,
        row = 1
    )
    async def auto_vc_enabled(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ):
        await self._toggle(
            interaction = interaction,
            toggler = toggle_auto_vc_module_enabled,
            label = 'Auto VC'
        )

    @discord.ui.button(
        label = 'Counting',
        style = discord.ButtonStyle.grey,
        row = 1
    )
    async def counting_enabled(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ):
        await self._toggle(
            interaction = interaction,
            toggler = toggle_counting_module_enabled,
            label = 'Counting'
        )

    @discord.ui.button(
        label = 'Games',
        style = discord.ButtonStyle.grey,
        row = 1
    )
    async def games_enabled(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ):
        await self._toggle(
            interaction = interaction,
            toggler = toggle_games_module_enabled,
            label = 'Games'
        )

    @discord.ui.button(
        label = 'Welcome Message',
        style = discord.ButtonStyle.grey,
        row = 1
    )
    async def welcome_message_enabled(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ):
        await self._toggle(
            interaction = interaction,
            toggler = toggle_welcome_status,
            label = 'Welcome Message'
        )
