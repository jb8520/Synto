from discord import Guild

def mention_user(guild: Guild, user_id: int) -> str:
    member = guild.get_member(user_id)
    return member.mention if member is not None else f'<@{user_id}>'