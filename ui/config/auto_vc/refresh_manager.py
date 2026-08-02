import discord

from .manager_embed import build_auto_vc_manager_embed

async def refresh_auto_vc_manager_message(
    guild: discord.Guild,
    message: discord.Message | None
) -> None:
    if message is None:
        return

    from .manager_view import AutoVcManagerView
    
    await message.edit(
        embed = build_auto_vc_manager_embed(
            guild = guild
        ),
        view = AutoVcManagerView(
            guild_id = guild.id
        )
    )