import discord

from database.repositories import (
    consume_user_save_if_available,
    reset_counting_progress,
    log_counting
)

from services.counting_saves_dataclass import CountingSaveRuntime, PendingCountBreak

from ui.views.premium import CountingSavesUpsellView


COUNTING_SAVE_WINDOW_SECONDS = 60


def _build_break_text(
    breaking_user_mention: str,
    broken_at_score: int,
    reason: str | None
) -> str:
    reason_text = f'{reason} ' if reason is not None else ''

    return (
        f'{breaking_user_mention} ruined the count at `{broken_at_score}`! '
        f'{reason_text}The next number is `1`.'
    )


class UseCountingSaveView(discord.ui.View):
    def __init__(
        self,
        runtime: CountingSaveRuntime,
        pending: PendingCountBreak
    ):
        super().__init__(timeout = COUNTING_SAVE_WINDOW_SECONDS)

        self.runtime = runtime
        self.pending = pending
        self.resolved = False
        self.message: discord.Message | None = None

    @discord.ui.button(
        label = 'Use Counting Save',
        style = discord.ButtonStyle.blurple,
        emoji = '💾'
    )
    async def use_save(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        if interaction.user.id != self.pending.breaking_user_id:
            await interaction.response.send_message(
                '❌ Only the person who broke the count can use a Counting Save.',
                ephemeral = True
            )
            return

        consumed = consume_user_save_if_available(self.pending.breaking_user_id)

        if not consumed:
            await interaction.response.send_message(
                '❌ You don\'t have any Counting Saves left.',
                view = CountingSavesUpsellView(),
                ephemeral = True
            )
            return

        self.resolved = True
        self.runtime.clear_pending_break(self.pending.guild_id)

        button.disabled = True

        await interaction.response.edit_message(
            content = (
                f'✅ {interaction.user.mention} used a Counting Save! '
                f'The count continues - the next number is `{self.pending.broken_at_score + 1}`.'
            ),
            view = self
        )

        log_counting(
            user_id = interaction.user.id,
            guild_id = self.pending.guild_id
        )

        self.stop()

    async def on_timeout(self) -> None:
        if self.resolved:
            return

        self.runtime.clear_pending_break(self.pending.guild_id)

        reset_counting_progress(self.pending.guild_id)

        for child in self.children:
            child.disabled = True

        if self.message is not None:
            try:
                await self.message.edit(
                    content = _build_break_text(
                        f'<@{self.pending.breaking_user_id}>',
                        self.pending.broken_at_score,
                        self.pending.reason
                    ),
                    view = self
                )

            except discord.HTTPException:
                pass

        log_counting(
            user_id = self.pending.breaking_user_id,
            guild_id = self.pending.guild_id
        )
