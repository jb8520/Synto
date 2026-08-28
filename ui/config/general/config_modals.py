import re

import discord

from database.repositories import set_general_embed_colour

from .. import SETTINGS_COLOUR


HEX_COLOUR_PATTERN = re.compile(r'^#?[0-9a-fA-F]{6}$')


class GeneralEmbedColourModal(discord.ui.Modal, title = 'Embed Colour'):
    colour_input = discord.ui.TextInput(
        label = 'Hex Colour',
        placeholder = '#00F3FF',
        min_length = 0,
        max_length = 7,
        required = False
    )

    async def on_submit(self, interaction: discord.Interaction):
        colour = self.colour_input.value.strip()

        await interaction.response.defer()

        if colour == '':
            set_general_embed_colour(
                guild_id = interaction.guild.id,
                colour = None
            )

            await interaction.followup.send(
                embed = discord.Embed(
                    description = 'Embed colour has been cleared - Synto will use its default colour again.',
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

        set_general_embed_colour(
            guild_id = interaction.guild.id,
            colour = normalised_colour
        )

        await interaction.followup.send(
            embed = discord.Embed(
                description = f'Embed colour has been set to `#{normalised_colour}`.',
                colour = int(normalised_colour, 16)
            ),
            ephemeral = True
        )
