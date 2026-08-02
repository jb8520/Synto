import discord

from database.models import CountingSettings

from database.repositories import (
    get_counting_settings,
    update_current_score,
    reset_counting_progress,
    log_counting,
)


COUNTING_SUCCESS_REACTION = '✅'
COUNTING_FAIL_REACTION = '❌'


def parse_count(content: str) -> int | None:
    try:
        return int(content.strip())

    except ValueError:
        return None


def build_counting_stats_embed(guild: discord.Guild) -> discord.Embed:
    settings = get_counting_settings(guild.id)

    counting_channel = guild.get_channel(settings.channel_id)

    if counting_channel is None:
        channel_text = '`Not set`'
    
    else:
        channel_text = counting_channel.mention

    return discord.Embed(
        title = 'Counting Stats',
        description = (
            f'Highscore: `{settings.highscore}`\n\n'
            f'Current Count: `{settings.current_score}`\n\n'
            f'Counting Channel: {channel_text}'
        ),
        colour = 0x00F3FF
    )


async def handle_counting_message(message: discord.Message) -> None:
    if message.guild is None:
        return

    if message.author.bot:
        return

    settings = get_counting_settings(message.guild.id)

    if settings.channel_id == 0:
        return

    if message.channel.id != settings.channel_id:
        return

    new_count = parse_count(message.content)

    if new_count is None:
        return

    expected_count = settings.current_score + 1

    if new_count != expected_count:
        await fail_count(
            message = message,
            settings = settings,
            reason = f'The next number was `{expected_count}`.'
        )
        return

    if (
        message.author.id == settings.last_author_id
        and not settings.double_count
    ):
        await fail_count(
            message = message,
            settings = settings,
            reason = 'You can\'t double count.'
        )
        return

    await pass_count(
        message = message,
        new_count = new_count
    )


async def pass_count(
    message: discord.Message,
    new_count: int
) -> None:
    if message.guild is None:
        return

    await message.add_reaction(COUNTING_SUCCESS_REACTION)

    update_current_score(
        guild_id = message.guild.id,
        current_score = new_count,
        last_message_id = message.id,
        last_author_id = message.author.id
    )

    log_counting(
        user_id = message.author.id,
        guild_id = message.guild.id
    )


async def fail_count(
    message: discord.Message,
    settings: CountingSettings,
    reason: str
) -> None:
    if message.guild is None:
        return

    reset_counting_progress(message.guild.id)

    await message.channel.send(
        f'{message.author.mention} ruined the count at `{settings.current_score}`! '
        f'{reason} The next number is **`1`**.'
    )

    await message.add_reaction(COUNTING_FAIL_REACTION)

    log_counting(
        user_id = message.author.id,
        guild_id = message.guild.id
    )


async def handle_deleted_counting_message(message: discord.Message) -> None:
    if message.guild is None:
        return

    if message.author.bot:
        return

    settings = get_counting_settings(message.guild.id)

    if settings.channel_id == 0:
        return

    if message.channel.id != settings.channel_id:
        return

    if message.id != settings.last_message_id:
        return

    await message.channel.send(
        f'{message.author.mention} deleted their count of `{settings.current_score}`. '
        f'The next number is **`{settings.current_score + 1}`**.'
    )

    log_counting(
        user_id = message.author.id,
        guild_id = message.guild.id
    )