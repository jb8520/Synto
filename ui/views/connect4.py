import discord

from utils.mention_user import mention_user


ROWS = 6
COLS = 7
CONNECT_N = 4

EMPTY = 0
PLAYER_1_TILE = 1
PLAYER_2_TILE = -1


class Connect4Select(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label = '1️⃣',
                value = '0'
            ),
            
            discord.SelectOption(
                label = '2️⃣',
                value = '1'
            ),

            discord.SelectOption(
                label = '3️⃣',
                value = '2'
            ),

            discord.SelectOption(
                label = '4️⃣',
                value = '3'
            ),

            discord.SelectOption(
                label = '5️⃣',
                value = '4'
            ),
            
            discord.SelectOption(
                label = '6️⃣',
                value = '5'
            ),

            discord.SelectOption(
                label = '7️⃣',
                value = '6'
            )
        ]

        super().__init__(
            placeholder = 'What column would you like to play?',
            min_values = 1,
            max_values = 1,
            options = options,
            custom_id = 'connect4_column_select'
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                '❌ This game can only be played in a server.',
                ephemeral = True
            )
            return

        view = self.view

        if not isinstance(view, Connect4View):
            await interaction.response.send_message(
                '❌ Something went wrong with this game.',
                ephemeral = True
            )
            return

        column_index = int(self.values[0])

        if view.player_turn == 1 and view.player_1 == 0:
            view.player_1 = interaction.user.id
            view.player_turn = 1

        elif view.player_turn == 2 and view.player_2 == 0:
            # if interaction.user.id == view.player_1:
            #     await interaction.response.send_message(
            #         f'❌ {interaction.user.mention} you cannot play against yourself.',
            #         ephemeral = True,
            #     )
            #     return
            
            view.player_2 = interaction.user.id
            view.player_turn = 2

        if view.player_turn == 1 and view.player_1 == interaction.user.id:
            tile = PLAYER_1_TILE
            view.player_turn = 2

            if view.player_2 == 0:
                next_player = 'Player 2'
            
            else:
                next_player = mention_user(interaction.guild, view.player_2)

        elif view.player_turn == 2 and view.player_2 == interaction.user.id:
            tile = PLAYER_2_TILE
            view.player_turn = 1
            
            next_player = mention_user(interaction.guild, view.player_1)

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

        row_index = view.get_next_open_row(column_index)

        if row_index is None:
            await interaction.response.send_message(
                '❌ That column is full.',
                ephemeral = True
            )
            return

        view.board[row_index][column_index] = tile

        if row_index == 0:
            self.options = [
                option
                for option in self.options
                if int(option.value) != column_index
            ]

        winner = view.check_winner()

        if winner is None:
            content = f'It is now {next_player}\'s turn.'
            message = f'{view.display_board()}\n{content}'

            await interaction.response.edit_message(
                content = message,
                view = view
            )
            return

        if winner == PLAYER_1_TILE:
            content = f'{mention_user(interaction.guild, view.player_1)} won!'

        elif winner == PLAYER_2_TILE:
            content = f'{mention_user(interaction.guild, view.player_2)} won!'

        else:
            content = 'It\'s a tie!'

        message = f'{view.display_board()}\n{content}'

        view.stop()
        view = None

        await interaction.response.edit_message(
            content = message,
            view = view
        )


class Connect4View(discord.ui.View):
    def __init__(self):
        super().__init__()

        self.board = [
            [EMPTY for _ in range(COLS)]
            for _ in range(ROWS)
        ]

        self.player_1 = 0
        self.player_2 = 0
        self.player_turn = 1

        self.add_item(Connect4Select())

    def display_board(self) -> str:
        message = ''

        for row in self.board:
            for tile in row:
                if tile == PLAYER_1_TILE:
                    message += '🔴'
                
                elif tile == PLAYER_2_TILE:
                    message += '🟡'
                
                else:
                    message += '⬛'

            message += '\n'

        message += '1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣'
        return message

    def get_next_open_row(self, column_index: int) -> int | None:
        for row_index in range(ROWS - 1, -1, -1):
            if self.board[row_index][column_index] == EMPTY:
                return row_index

        return None

    def check_winner(self) -> int | None:
        directions = [
            (0, 1),   # horizontal
            (1, 0),   # vertical
            (1, 1),   # diagonal down-right
            (1, -1),  # diagonal down-left
        ]

        for row in range(ROWS):
            for col in range(COLS):
                tile = self.board[row][col]

                if tile == EMPTY:
                    continue

                for row_step, col_step in directions:
                    if self.has_connect_n(row, col, row_step, col_step, tile):
                        return tile

        if all(tile != EMPTY for row in self.board for tile in row):
            return 0

        return None

    def has_connect_n(
        self,
        start_row: int,
        start_col: int,
        row_step: int,
        col_step: int,
        tile: int,
    ) -> bool:
        for offset in range(CONNECT_N):
            row = start_row + row_step * offset
            col = start_col + col_step * offset

            if not 0 <= row < ROWS:
                return False

            if not 0 <= col < COLS:
                return False

            if self.board[row][col] != tile:
                return False

        return True