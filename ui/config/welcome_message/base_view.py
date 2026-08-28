import discord

from checks.permissions import admin_only_interaction

from database.repositories import (
    get_welcome_message_settings,
    reset_welcome_message_settings
)

from ..common import BaseSettingsView

from .. import SETTINGS_COLOUR

from .embed import (
    build_welcome_message_embed,
    build_welcome_preview_embed
)

from .config_views import WelcomeChannelView

from .config_modals import(
    WelcomeTitleModal,
    WelcomeDescriptionModal,
    WelcomeColourModal
)


class WelcomeMessageMenuView(BaseSettingsView):
    information_title = 'Welcome Message Settings Information ℹ️'

    information_fields = [
        (
            'Welcome Channel',
            '> The channel where welcome messages will be sent.'
        ),
        (
            'Title',
            '> The title shown at the top of the welcome message embed. You can use `{server}` for the server name, `{member}` to mention the new member, and `{member_name}` for the new member\'s display name.'
        ),
        (
            'Description',
            '> The main welcome message text. You can use `{server}` for the server name, `{member}` to mention the new member, and `{member_name}` for the new member\'s display name.'
        ),
        (
            'Colour',
            '> The embed colour for the welcome message. Use a hex colour such as `#00F3FF`.'
        ),
        (
            'Preview',
            '> Sends an ephemeral preview of the currently configured welcome message.'
        ),
        (
            'Reset',
            '> Resets the welcome message channel, title, description, colour, and status back to their defaults.'
        )
    ]


    @discord.ui.button(
        label = 'Welcome Channel',
        style = discord.ButtonStyle.grey,
        row = 0
    )
    async def welcome_channel(
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

        settings = get_welcome_message_settings(interaction.guild.id)

        if settings.channel_id == 0:
            channel = '`Not set`'
        else:
            discord_channel = interaction.guild.get_channel(settings.channel_id)
            channel = (
                discord_channel.mention
                if discord_channel is not None
                else '`Unknown channel`'
            )

        view = WelcomeChannelView()

        await interaction.followup.send(
            embed = discord.Embed(
                description = f'The welcome channel is currently set to {channel}.',
                colour = SETTINGS_COLOUR
            ),
            view = view,
            ephemeral = True
        )

        await view.wait()

        await interaction.message.edit(
            embed = build_welcome_message_embed(interaction),
            view = WelcomeMessageMenuView()
        )


    @discord.ui.button(
        label = 'Title',
        style = discord.ButtonStyle.grey,
        row = 0
    )
    async def title(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        title_modal = WelcomeTitleModal()

        await interaction.response.send_modal(title_modal)

        await title_modal.wait()

        await interaction.message.edit(
            embed = build_welcome_message_embed(interaction),
            view = WelcomeMessageMenuView()
        )


    @discord.ui.button(
        label = 'Description',
        style = discord.ButtonStyle.grey,
        row = 1
    )
    async def description(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        description_modal = WelcomeDescriptionModal()

        await interaction.response.send_modal(description_modal)

        await description_modal.wait()

        await interaction.message.edit(
            embed = build_welcome_message_embed(interaction),
            view = WelcomeMessageMenuView()
        )


    @discord.ui.button(
        label = 'Colour',
        style = discord.ButtonStyle.grey,
        row = 1
    )
    async def colour(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        colour_modal = WelcomeColourModal()

        await interaction.response.send_modal(colour_modal)

        await colour_modal.wait()

        await interaction.message.edit(
            embed = build_welcome_message_embed(interaction),
            view = WelcomeMessageMenuView()
        )

    @discord.ui.button(
        label = 'Preview',
        style = discord.ButtonStyle.blurple,
        row = 2
    )
    async def preview(
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

        settings = get_welcome_message_settings(interaction.guild.id)

        preview_embed = build_welcome_preview_embed(
            interaction = interaction,
            member = interaction.user,
            title = settings.title,
            description = settings.description,
            colour = settings.colour
        )

        await interaction.followup.send(
            content = f'Preview welcome message for {interaction.user.mention}:',
            embed = preview_embed,
            ephemeral = True,
        )

    @discord.ui.button(
        label = 'Reset',
        style = discord.ButtonStyle.red,
        row = 2
    )
    async def reset(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        reset_welcome_message_settings(interaction.guild.id)

        await interaction.response.edit_message(
            embed = build_welcome_message_embed(interaction),
            view = WelcomeMessageMenuView()
        )

        await interaction.followup.send(
            embed = discord.Embed(
                description = 'Welcome message settings have been reset to their defaults.',
                colour = SETTINGS_COLOUR
            ),
            ephemeral = True
        )