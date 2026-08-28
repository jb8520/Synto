import discord

from discord.ext import commands

from settings import settings

from database.repositories import user_has_active_premium_purchase


SUPPORTER_ROLE_GRANT_REASON = 'Synto Premium supporter'


async def _grant_role(
    guild: discord.Guild,
    member: discord.Member,
    role: discord.Role
) -> None:
    if role in member.roles:
        return

    try:
        await member.add_roles(role, reason = SUPPORTER_ROLE_GRANT_REASON)

        print(f'✅ Granted Supporter role to user_id={member.id} in the support server')

    except discord.HTTPException as error:
        print(
            f'⚠️ Failed to grant Supporter role to user_id={member.id}\n'
            f'{type(error).__name__}: {error}'
        )


async def grant_supporter_role_if_missing(
    bot: commands.Bot,
    user_id: int
) -> None:
    """Called right after a premium purchase is recorded as active. If the
    buyer isn't currently a member of the support server, this silently
    does nothing - handle_support_server_member_join() covers them if/when
    they join later."""
    if settings.support_server_id is None or settings.supporter_role_id is None:
        return

    guild = bot.get_guild(settings.support_server_id)

    if guild is None:
        return

    member = guild.get_member(user_id)

    if member is None:
        return

    role = guild.get_role(settings.supporter_role_id)

    if role is None:
        return

    await _grant_role(guild = guild, member = member, role = role)


async def handle_support_server_member_join(
    bot: commands.Bot,
    member: discord.Member
) -> None:
    """Backstop for the case above: someone buys Premium before ever
    joining the support server, or while the role-grant attempt failed.
    Runs on every join to the support server specifically."""
    if settings.support_server_id is None or settings.supporter_role_id is None:
        return

    if member.guild.id != settings.support_server_id:
        return

    if not user_has_active_premium_purchase(member.id):
        return

    role = member.guild.get_role(settings.supporter_role_id)

    if role is None:
        return

    await _grant_role(guild = member.guild, member = member, role = role)
