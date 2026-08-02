import re

import discord

from database.repositories.welcome_message import (
    set_welcome_title,
    set_welcome_description,
    set_welcome_colour,
    clear_welcome_description,
    clear_welcome_colour
)

from .. import SETTINGS_COLOUR


HEX_COLOUR_PATTERN = re.compile(r'^#?[0-9a-fA-F]{6}$')


class WelcomeTitleModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(
            title = 'Welcome Message Title'
        )

        self.title_input = discord.ui.TextInput(
            label = 'Title',
            placeholder = 'Welcome!',
            min_length = 1,
            max_length = 256,
            required = True
        )

        self.add_item(self.title_input)

    async def on_submit(self, interaction: discord.Interaction):
        title = self.title_input.value.strip()

        await interaction.response.defer()

        set_welcome_title(
            guild_id = interaction.guild.id,
            title = title,
        )

        await interaction.followup.send(
            embed = discord.Embed(
                description = f'Welcome message title has been set to `{title}`.',
                colour = SETTINGS_COLOUR
            ),
            ephemeral = True
        )


class WelcomeDescriptionModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(
            title = 'Welcome Message Description'
        )

        self.description_input = discord.ui.TextInput(
            label = 'Description',
            placeholder = 'Welcome to {server}, {member}!',
            style = discord.TextStyle.paragraph,
            min_length = 0,
            max_length = 4000,
            required = False
        )

        self.add_item(self.description_input)

    async def on_submit(self, interaction: discord.Interaction):
        description = self.description_input.value.strip()

        await interaction.response.defer()

        if description == '':
            clear_welcome_description(guild_id = interaction.guild.id)

            await interaction.followup.send(
                embed = discord.Embed(
                    description = 'Welcome message description has been cleared.',
                    colour = SETTINGS_COLOUR
                ),
                ephemeral = True
            )
            return

        set_welcome_description(
            guild_id = interaction.guild.id,
            description = description
        )

        await interaction.followup.send(
            embed = discord.Embed(
                description = 'Welcome message description has been updated.',
                colour = SETTINGS_COLOUR
            ),
            ephemeral = True
        )


class WelcomeColourModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(
            title = 'Welcome Message Colour'
        )

        self.colour_input = discord.ui.TextInput(
            label = 'Hex Colour',
            placeholder = '#00F3FF',
            min_length = 0,
            max_length = 7,
            required = False
        )

        self.add_item(self.colour_input)

    async def on_submit(self, interaction: discord.Interaction):
        colour = self.colour_input.value.strip()

        await interaction.response.defer()

        if colour == '':
            clear_welcome_colour(guild_id = interaction.guild.id)

            await interaction.followup.send(
                embed = discord.Embed(
                    description = 'Welcome message colour has been cleared.',
                    colour = SETTINGS_COLOUR
                ),
                ephemeral = True
            )
            return

        if HEX_COLOUR_PATTERN.fullmatch(colour) is None:
            await interaction.followup.send(
                embed = discord.Embed(
                    description = 'Please enter a valid hex colour, such as `#00F3FF` or `00F3FF`.',
                    colour = SETTINGS_COLOUR
                ),
                ephemeral = True
            )
            return

        normalised_colour = colour.removeprefix('#').upper()

        set_welcome_colour(
            guild_id = interaction.guild.id,
            colour = normalised_colour
        )

        await interaction.followup.send(
            embed = discord.Embed(
                description = f'Welcome message colour has been set to `#{normalised_colour}`.',
                colour = SETTINGS_COLOUR
            ),
            ephemeral = True
        )