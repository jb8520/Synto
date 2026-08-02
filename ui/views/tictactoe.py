import discord

from utils.mention_user import mention_user


BOARD_SIZE = 3

EMPTY = 0
X_TILE = 1
O_TILE = -1


class TicTacToeButton(discord.ui.Button['TicTacToeView']):
    def __init__(self, x: int, y: int):
        super().__init__(
            style = discord.ButtonStyle.grey,
            label = '\u200b',
            row = y,
        )

        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                '❌ This game can only be played in a server.',
                ephemeral = True,
            )
            return

        view = self.view

        if not isinstance(view, TicTacToeView):
            await interaction.response.send_message(
                '❌ Something went wrong with this game.',
                ephemeral = True,
            )
            return

        if view.player_turn == 1 and view.player_1 == 0:
            view.player_1 = interaction.user.id
            view.player_turn = 1

        elif view.player_turn == 2 and view.player_2 == 0:
            # if interaction.user.id == view.player_1:
            #     await interaction.response.send_message(
            #         f'❌ {interaction.user.mention} you cannot play against yourself.',
            #         ephemeral=True,
            #     )
            #     return

            view.player_2 = interaction.user.id
            view.player_turn = 2

        if view.player_turn == 1 and view.player_1 == interaction.user.id:
            self.style = discord.ButtonStyle.red
            self.label = 'X'
            self.disabled = True

            view.board[self.y][self.x] = X_TILE
            view.player_turn = 2

            if view.player_2 == 0:
                next_player = 'Player 2'
            
            else:
                next_player = f'{mention_user(interaction.guild, view.player_2)}'

        elif view.player_turn == 2 and view.player_2 == interaction.user.id:
            self.style = discord.ButtonStyle.green
            self.label = 'O'
            self.disabled = True

            view.board[self.y][self.x] = O_TILE
            view.player_turn = 1

            next_player = f'{mention_user(interaction.guild, view.player_1)}'

        else:
            is_player_in_game = interaction.user.id in {view.player_1, view.player_2}

            if is_player_in_game:
                message = '❌ it is not your turn.'
            
            else:
                message = '❌ this is not your game.'

            await interaction.response.send_message(
                f'{interaction.user.mention} {message}',
                ephemeral = True,
            )
            return

        winner = view.check_winner()

        if winner is None:
            content = f'It is now {next_player}\'s turn.'
            message = f'{view.display_board()}\n{content}'

            await interaction.response.edit_message(
                content = content,
                view = view,
            )
            return
        
        if winner == X_TILE:
            content = f'{mention_user(interaction.guild, view.player_1)} won!'

        elif winner == O_TILE:
            content = f'{mention_user(interaction.guild, view.player_2)} won!'

        else:
            content = 'It\'s a tie!'

        view.stop()
        for child in view.children:
            child.disabled = True

        await interaction.response.edit_message(
            content = content,
            view = view
        )


class TicTacToeView(discord.ui.View):
    children: list[TicTacToeButton]

    def __init__(self):
        super().__init__()

        self.board = [
            [EMPTY for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]

        self.player_1 = 0
        self.player_2 = 0
        self.player_turn = 1

        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                self.add_item(TicTacToeButton(x, y))

    def check_winner(self) -> int | None:
        lines = []

        # Rows
        lines.extend(self.board)

        # Columns
        for x in range(BOARD_SIZE):
            lines.append([
                self.board[y][x]
                for y in range(BOARD_SIZE)
            ])

        # Diagonals
        lines.append([
            self.board[i][i]
            for i in range(BOARD_SIZE)
        ])

        lines.append([
            self.board[i][BOARD_SIZE - 1 - i]
            for i in range(BOARD_SIZE)
        ])

        for line in lines:
            value = sum(line)

            if value == BOARD_SIZE:
                return X_TILE

            if value == -BOARD_SIZE:
                return O_TILE

        if all(tile != EMPTY for row in self.board for tile in row):
            return 0

        return None

