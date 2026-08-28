import discord

from checks.permissions import auto_vc_owner_interaction

from services.auto_vc import (
    claim_auto_vc_ownership,
    kick_members_from_owned_auto_vc,
    permit_targets_to_owned_auto_vc,
    set_owned_auto_vc_connect_permission,
    set_owned_auto_vc_view_permission
)

from ui.modals.auto_vc import (
    RenameModal,
    UserLimitModal
)



class KickView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = 120)
        self.add_item(KickSelect())


class KickSelect(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(
            placeholder = 'Select members to kick',
            min_values = 1,
            max_values = 25,
            custom_id = 'auto_vc_kick_select'
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ) -> None:
        allowed, error_message = auto_vc_owner_interaction(interaction)

        if not allowed:
            await interaction.response.send_message(
                error_message,
                ephemeral = True
            )
            return

        members = [
            value
            for value in self.values
            if isinstance(value, discord.Member)
        ]

        _, message = await kick_members_from_owned_auto_vc(
            runtime = interaction.client.auto_vc_runtime,
            interaction = interaction,
            members = members
        )

        await interaction.response.edit_message(
            content = message,
            view = None
        )


class InviteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = 120)
        self.add_item(InviteSelect())


class InviteSelect(discord.ui.MentionableSelect):
    def __init__(self):
        super().__init__(
            placeholder = 'Select members or roles to permit',
            min_values = 1,
            max_values = 25,
            custom_id = 'auto_vc_invite_select'
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ) -> None:
        allowed, error_message = auto_vc_owner_interaction(interaction)

        if not allowed:
            await interaction.response.send_message(
                error_message,
                ephemeral = True
            )
            return

        targets = [
            value
            for value in self.values
            if isinstance(value, discord.Member | discord.Role)
        ]

        _, message = await permit_targets_to_owned_auto_vc(
            runtime = interaction.client.auto_vc_runtime,
            interaction = interaction,
            targets = targets
        )

        await interaction.response.edit_message(
            content = message,
            view = None
        )


class AutoVcButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)

    @discord.ui.button(
        emoji = '<:Lock:1167457451134701649>',
        style = discord.ButtonStyle.grey,
        custom_id = 'auto_vc_lock',
        row = 0
    )
    async def lock(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ) -> None:
        allowed, error_message = auto_vc_owner_interaction(interaction)

        if not allowed:
            await interaction.response.send_message(
                error_message,
                ephemeral = True
            )
            return

        _, message = await set_owned_auto_vc_connect_permission(
            runtime = interaction.client.auto_vc_runtime,
            interaction = interaction,
            can_connect = False
        )

        await interaction.response.send_message(
            message,
            ephemeral = True
        )

    @discord.ui.button(
        emoji = '<:Unlock:1177249846105755718>',
        style = discord.ButtonStyle.grey,
        custom_id = 'auto_vc_unlock',
        row = 0
    )
    async def unlock(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ) -> None:
        allowed, error_message = auto_vc_owner_interaction(interaction)

        if not allowed:
            await interaction.response.send_message(
                error_message,
                ephemeral = True
            )
            return

        _, message = await set_owned_auto_vc_connect_permission(
            runtime = interaction.client.auto_vc_runtime,
            interaction = interaction,
            can_connect = True
        )

        await interaction.response.send_message(
            message,
            ephemeral = True
        )

    @discord.ui.button(
        emoji = '<:Claim:1174656588338954311>',
        style = discord.ButtonStyle.grey,
        custom_id = 'auto_vc_claim',
        row = 0
    )
    async def claim(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ) -> None:
        _, message = await claim_auto_vc_ownership(
            runtime = interaction.client.auto_vc_runtime,
            interaction = interaction
        )

        await interaction.response.send_message(
            message,
            ephemeral = True
        )

    @discord.ui.button(
        emoji = '<:Hide:1167457445082308638>',
        style = discord.ButtonStyle.grey,
        custom_id = 'auto_vc_hide',
        row = 1
    )
    async def hide(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ) -> None:
        allowed, error_message = auto_vc_owner_interaction(interaction)

        if not allowed:
            await interaction.response.send_message(
                error_message,
                ephemeral = True
            )
            return

        _, message = await set_owned_auto_vc_view_permission(
            runtime = interaction.client.auto_vc_runtime,
            interaction = interaction,
            can_view = False
        )

        await interaction.response.send_message(
            message,
            ephemeral = True
        )

    @discord.ui.button(
        emoji = '<:Show:1167457420004577370>',
        style = discord.ButtonStyle.grey,
        custom_id = 'auto_vc_show',
        row = 1
    )
    async def show(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ) -> None:
        allowed, error_message = auto_vc_owner_interaction(interaction)

        if not allowed:
            await interaction.response.send_message(
                error_message,
                ephemeral = True
            )
            return

        _, message = await set_owned_auto_vc_view_permission(
            runtime = interaction.client.auto_vc_runtime,
            interaction = interaction,
            can_view = True
        )

        await interaction.response.send_message(
            message,
            ephemeral = True
        )

    @discord.ui.button(
        emoji = '<:Rename:1167457460852891748>',
        style = discord.ButtonStyle.grey,
        custom_id = 'auto_vc_rename',
        row = 1
    )
    async def rename(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ) -> None:
        allowed, error_message = auto_vc_owner_interaction(interaction)

        if not allowed:
            await interaction.response.send_message(
                error_message,
                ephemeral = True
            )
            return

        await interaction.response.send_modal(RenameModal())

    @discord.ui.button(
        emoji = '<:Kick:1386150479804764280>',
        style = discord.ButtonStyle.grey,
        custom_id = 'auto_vc_kick',
        row = 2
    )
    async def kick(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ) -> None:
        allowed, error_message = auto_vc_owner_interaction(interaction)

        if not allowed:
            await interaction.response.send_message(
                error_message,
                ephemeral = True
            )
            return

        await interaction.response.send_message(
            'Select the members you want to kick from your voice channel.',
            view = KickView(),
            ephemeral = True
        )

    @discord.ui.button(
        emoji = '<:Invite:1386150477846020136>',
        style = discord.ButtonStyle.grey,
        custom_id = 'auto_vc_invite',
        row = 2
    )
    async def invite(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ) -> None:
        allowed, error_message = auto_vc_owner_interaction(interaction)

        if not allowed:
            await interaction.response.send_message(
                error_message,
                ephemeral = True
            )
            return

        await interaction.response.send_message(
            'Select the members or roles you want to give access to your voice channel.',
            view = InviteView(),
            ephemeral = True
        )

    @discord.ui.button(
        emoji = '<:Users:1386150481138810960>',
        style = discord.ButtonStyle.grey,
        custom_id = 'auto_vc_limit',
        row = 2
    )
    async def user_limit(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button
    ) -> None:
        allowed, error_message = auto_vc_owner_interaction(interaction)

        if not allowed:
            await interaction.response.send_message(
                error_message,
                ephemeral = True
            )
            return

        await interaction.response.send_modal(UserLimitModal())