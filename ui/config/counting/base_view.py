import discord

from checks.permissions import admin_only_interaction

from database.repositories import (
    get_counting_settings,
    toggle_double_count,
    toggle_counting_saves_enabled
)

from ..common import BaseSettingsView

from .. import SETTINGS_COLOUR, get_settings_colour

from .embed import build_counting_embed

from .config_views import CountingChannelView


class CountingMenuView(BaseSettingsView):
    information_title = 'Counting Settings Information ℹ️'

    information_fields = [
        (
            'Counting Channel',
            '> The channel where members can use the counting feature.',
        ),
        (
            'Double Count',
            '> Whether members can count multiple times in a row.',
        ),
        (
            'Counting Saves',
            '> Whether members can use their own Counting Saves to rescue a broken count. '
            'Enabled by default - Counting Saves are owned by the member, not this server.',
        ),
    ]


    @discord.ui.button(
        label = 'Counting Channel',
        style = discord.ButtonStyle.grey,
        row = 0
    )
    async def counting_channel(
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

        settings = get_counting_settings(interaction.guild.id)

        if settings.channel_id == 0:
            channel = '#channel'
        
        else:
            discord_channel = interaction.guild.get_channel(settings.channel_id)
            channel = discord_channel.mention if discord_channel is not None else '#channel'

        view = CountingChannelView()

        await interaction.followup.send(
            embed = discord.Embed(
                description = f'The counting channel is currently set to {channel}',
                colour = SETTINGS_COLOUR
            ),
            view = view,
            ephemeral = True
        )

        await view.wait()

        await interaction.message.edit(
            embed = build_counting_embed(interaction),
            view = CountingMenuView()
        )
    

    @discord.ui.button(
        label = 'Double Count',
        style = discord.ButtonStyle.grey,
        row = 0
    )
    async def double_count(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        new_value = toggle_double_count(interaction.guild.id)

        await interaction.response.edit_message(
            embed = build_counting_embed(interaction),
            view = CountingMenuView()
        )

        await interaction.followup.send(
            embed = discord.Embed(
                description = f'Double counting has been set to `{new_value}`.',
                colour = get_settings_colour(interaction.guild.id)
            ),
            ephemeral = True
        )


    @discord.ui.button(
        label = 'Counting Saves',
        style = discord.ButtonStyle.grey,
        row = 0
    )
    async def counting_saves_enabled(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        new_value = toggle_counting_saves_enabled(interaction.guild.id)

        await interaction.response.edit_message(
            embed = build_counting_embed(interaction),
            view = CountingMenuView()
        )

        await interaction.followup.send(
            embed = discord.Embed(
                description = f'Counting Saves have been set to `{new_value}`.',
                colour = get_settings_colour(interaction.guild.id)
            ),
            ephemeral = True
        )