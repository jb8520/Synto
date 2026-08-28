import discord

from checks.permissions import admin_only_interaction

from . import get_settings_colour


def build_main_menu_embed(guild_id: int) -> discord.Embed:
    embed = discord.Embed(
        title='Synto Settings ⚙️',
        description=(
            'Use the dropdown below to configure Synto for this server.\n\n'
            'Each section contains its own settings and information button.'
        ),
        colour=get_settings_colour(guild_id),
    )

    embed.add_field(
        name='🛠️ General',
        value='> Configure admin roles, feature toggles, the updates channel, and embed colour.',
        inline=False,
    )

    embed.add_field(
        name='🔢 Counting',
        value='> Configure the counting channel and double-counting rules.',
        inline=False,
    )

    embed.add_field(
        name='🔊 Auto VCs',
        value='> Configure automatic voice channel creation and permissions.',
        inline=False,
    )

    embed.add_field(
        name='👋 Welcome Message',
        value='> Configure the server welcome message.',
        inline=False,
    )

    return embed


class ConfigMenuView(discord.ui.View):
    def __init__(self, timeout = None):
        super().__init__(timeout = timeout)
        self.add_item(ConfigSelectMenu())


class ConfigSelectMenu(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label = 'Menu',
                value = 'menu',
                description = 'Return to the main settings menu',
                emoji = '⚙️'
            ),
            discord.SelectOption(
                label = 'General',
                value = 'general',
                description = 'Configure general server settings',
                emoji = '🛠️'
            ),
            discord.SelectOption(
                label = 'Counting',
                value = 'counting',
                description = 'Configure the counting game',
                emoji = '🔢'
            ),
            discord.SelectOption(
                label = 'Auto VCs',
                value = 'auto_vcs',
                description = 'Configure automatic voice channels',
                emoji = '🔊'
            ),
            discord.SelectOption(
                label = 'Welcome Message',
                value = 'welcome_message',
                description = 'Configure welcome messages',
                emoji = '👋'
            )
        ]

        super().__init__(
            placeholder = 'Settings Options',
            min_values = 1,
            max_values = 1,
            options = options,
            row = 4
        )


    async def callback(self, interaction: discord.Interaction):
        allowed, _ = await admin_only_interaction(interaction)

        if not allowed:
            return

        await interaction.response.defer()

        selected_option = self.values[0]

        if selected_option == 'menu':
            await interaction.message.edit(
                content = None,
                embed = build_main_menu_embed(interaction.guild.id),
                view = ConfigMenuView(),
            )
            return
        

        if selected_option == 'general':
            from .general.router import open_general_config

            await open_general_config(interaction = interaction)

            return


        if selected_option == 'auto_vcs':
            from .auto_vc.router import open_auto_vc_config

            await open_auto_vc_config(interaction = interaction)

            return
        

        if selected_option == 'counting':
            from .counting.router import open_counting_config

            await open_counting_config(interaction = interaction)

            return


        if selected_option == 'welcome_message':
            from .welcome_message.router import open_welcome_message_config

            await open_welcome_message_config(interaction = interaction)

            return