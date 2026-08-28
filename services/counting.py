import discord

from datetime import datetime, timedelta, UTC

from database.models import CountingSettings

from database.repositories import (
    get_counting_settings,
    get_general_settings,
    get_user_save_balance,
    advance_count_if_unchanged,
    update_highscore_if_needed,
    reset_counting_progress,
    log_counting,
)

from services.counting_saves_dataclass import CountingSaveRuntime

from ui.config import get_settings_colour


COUNTING_SUCCESS_REACTION = '✅'
COUNTING_FAIL_REACTION = '❌'
COUNTING_PENDING_REACTION = '⚠️'

COUNTING_SAVE_WINDOW_SECONDS = 60


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
        colour = get_settings_colour(guild.id)
    )


async def handle_counting_message(
    runtime: CountingSaveRuntime,
    message: discord.Message
) -> None:
    if message.guild is None:
        return

    if message.author.bot:
        return

    if not get_general_settings(message.guild.id).counting_enabled:
        return

    settings = get_counting_settings(message.guild.id)

    if settings.channel_id == 0:
        return

    if message.channel.id != settings.channel_id:
        return

    # While a break is pending a Counting Save decision, the "real" count
    # is ambiguous (it might still be saved) - hold off on processing
    # anything else until it resolves.
    if runtime.get_pending_break(message.guild.id) is not None:
        return

    new_count = parse_count(message.content)

    if new_count is None:
        return

    expected_count = settings.current_score + 1

    if new_count != expected_count:
        await _handle_break(
            runtime = runtime,
            message = message,
            settings = settings
        )
        return

    if (
        message.author.id == settings.last_author_id
        and not settings.double_count
    ):
        await _handle_break(
            runtime = runtime,
            message = message,
            settings = settings,
            reason = 'You can\'t double count.'
        )
        return

    await pass_count(
        message = message,
        settings = settings,
        new_count = new_count
    )


async def pass_count(
    message: discord.Message,
    settings: CountingSettings,
    new_count: int
) -> None:
    if message.guild is None:
        return

    # Atomic compare-and-swap: only accept this count if current_score is
    # still what we read it as. Guards against two users posting the same
    # next number at almost the same time both being accepted as correct.
    advanced = advance_count_if_unchanged(
        guild_id = message.guild.id,
        expected_current_score = settings.current_score,
        new_score = new_count,
        last_message_id = message.id,
        last_author_id = message.author.id
    )

    if not advanced:
        # Lost a race to someone else's message - not offered a Counting
        # Save, this is a different failure mode from posting a wrong
        # number or double counting.
        await fail_count(
            message = message,
            settings = get_counting_settings(message.guild.id)
        )
        return

    update_highscore_if_needed(guild_id = message.guild.id)

    await message.add_reaction(COUNTING_SUCCESS_REACTION)

    log_counting(
        user_id = message.author.id,
        guild_id = message.guild.id
    )


def build_break_text(
    breaking_user_mention: str,
    broken_at_score: int,
    reason: str | None
) -> str:
    reason_text = f'{reason} ' if reason is not None else ''

    return (
        f'{breaking_user_mention} ruined the count at `{broken_at_score}`! '
        f'{reason_text}The next number is `1`.'
    )


async def fail_count(
    message: discord.Message,
    settings: CountingSettings,
    reason: str | None = None
) -> None:
    if message.guild is None:
        return

    reset_counting_progress(message.guild.id)

    await message.channel.send(
        build_break_text(message.author.mention, settings.current_score, reason)
    )

    await message.add_reaction(COUNTING_FAIL_REACTION)

    log_counting(
        user_id = message.author.id,
        guild_id = message.guild.id
    )


async def _handle_break(
    runtime: CountingSaveRuntime,
    message: discord.Message,
    settings: CountingSettings,
    reason: str = None
) -> None:
    if message.guild is None:
        return

    if not settings.counting_saves_enabled:
        await fail_count(message = message, settings = settings, reason = reason)
        return

    pending = runtime.start_pending_break(
        guild_id = message.guild.id,
        breaking_user_id = message.author.id,
        broken_at_score = settings.current_score,
        reason = reason
    )

    if pending is None:
        # A break is already pending for this guild - shouldn't happen
        # given the check in handle_counting_message, but fail safe.
        await fail_count(message = message, settings = settings, reason = reason)
        return

    # Imported here (rather than at module level) to avoid a circular
    # import - the view only depends on database.repositories, not on
    # this module, but this module does need to construct the view.
    from ui.views.counting_save import UseCountingSaveView

    balance = get_user_save_balance(message.author.id)
    reason_text = f'{reason} ' if reason is not None else ''

    expires_at = datetime.now(UTC) + timedelta(seconds = COUNTING_SAVE_WINDOW_SECONDS)
    expires_timestamp = int(expires_at.timestamp())

    view = UseCountingSaveView(runtime = runtime, pending = pending)

    sent_message = await message.channel.send(
        f'⚠️ {message.author.mention} broke the count at `{settings.current_score}`! {reason_text}'
        f'You have `{balance}` Counting Save{"s" if balance != 1 else ""} - '
        f'use one <t:{expires_timestamp}:R> to keep the count going.',
        view = view
    )

    view.message = sent_message

    await message.add_reaction(COUNTING_PENDING_REACTION)


async def handle_deleted_counting_message(message: discord.Message) -> None:
    if message.guild is None:
        return

    if message.author.bot:
        return

    if not get_general_settings(message.guild.id).counting_enabled:
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
