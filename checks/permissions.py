import discord
from discord.ext import commands

from settings import settings

from database.repositories import get_auto_vc_settings, get_general_admin_role_ids

from services.auto_vc_dataclass import AutoVcRuntime



def bot_owner_ctx(ctx: commands.Context) -> bool:
    return ctx.author.id == settings.bot_owner_id


async def admin_only_interaction(interaction: discord.Interaction) -> tuple[bool, str]:
    if (
        interaction.user.guild_permissions.administrator
        or interaction.user.id == settings.bot_owner_id
    ):
        return True, '✅ Success!'

    if interaction.guild is not None:
        admin_role_ids = set(get_general_admin_role_ids(interaction.guild.id))

        if any(role.id in admin_role_ids for role in interaction.user.roles):
            return True, '✅ Success!'

    error_message = '❌ You need to have the administrator permission to use this feature.'
    
    await interaction.response.send_message(
        error_message,
        ephemeral = True
    )
    
    return False, error_message


def auto_vc_owner_interaction(
    interaction: discord.Interaction
) -> tuple[bool, str]:
    if interaction.guild is None:
        return False, '❌ This can only be used in a server.'

    if not isinstance(interaction.user, discord.Member):
        return False, '❌ This can only be used in a server.'

    if interaction.user.voice is None:
        return False, '❌ You need to be in an Auto VC to use this.'

    if interaction.user.voice.channel is None:
        return False, '❌ You need to be in an Auto VC to use this.'

    runtime: AutoVcRuntime | None = getattr(
        interaction.client,
        'auto_vc_runtime',
        None
    )

    if runtime is None:
        return False, '❌ Auto VC runtime is not available.'

    temp_vc = runtime.find_by_channel(
        guild_id = interaction.guild.id,
        channel_id = interaction.user.voice.channel.id
    )

    if temp_vc is None:
        return False, '❌ You need to be in an Auto VC to use this.'

    if temp_vc.owner_id == interaction.user.id:
        return True, ''

    settings = get_auto_vc_settings(
        auto_vc_id = temp_vc.generator_id
    )

    if settings is None:
        return False, '❌ This Auto VC setup no longer exists.'

    moderator_role_ids = set(settings.moderator_role_ids)

    if any(role.id in moderator_role_ids for role in interaction.user.roles):
        return True, ''

    return False, '❌ You need to own this Auto VC to use this.'