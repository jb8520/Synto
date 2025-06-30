import discord

from discord import app_commands
from discord.ext import commands


class Connect_4_Select_Menu(discord.ui.Select):
    def __init__(self):
        Options=[
            discord.SelectOption(label='1️⃣',value=0),
            discord.SelectOption(label='2️⃣',value=1),
            discord.SelectOption(label='3️⃣',value=2),
            discord.SelectOption(label='4️⃣',value=3),
            discord.SelectOption(label='5️⃣',value=4),
            discord.SelectOption(label='6️⃣',value=5),
            discord.SelectOption(label='7️⃣',value=6),
        ]
        super().__init__(placeholder='What column would you like to play?',min_values=1,max_values=1,options=Options,custom_id='select_menu_connect4')
    
    async def callback(self,interaction:discord.Interaction):
        x=int(self.values[0])
        view:view.Connect_4_View=self.view #type:ignore
        if view.current_player==view.player_1==0:
            view.player_1=view.current_player=interaction.user.id
        elif view.current_player==view.player_2==0:
            if interaction.user.id==view.player_1:
                await interaction.response.send_message(f'❌ {interaction.user.mention} you can not play against yourself.',ephemeral=True)
                return
            view.player_2=view.current_player=interaction.user.id
        
        if view.current_player==view.player_1==interaction.user.id:
            value=1
            view.current_player=view.player_2
            if view.player_2==0:
                other_player='Player 2'
            else:
                other_player=interaction.guild.get_member(view.player_2).mention
        elif view.current_player==view.player_2==interaction.user.id:
            value=-1
            view.current_player=view.player_1
            other_player=interaction.guild.get_member(view.player_1).mention
        else:
            if view.current_player==view.player_1 and view.player_2==interaction.user.id or view.current_player==view.player_2 and view.player_1==interaction.user.id:
                message='❌ it is not your turn.' 
            else:
                message='❌ this is not your game.'
            await interaction.response.send_message(f'{interaction.user.mention} {message}',ephemeral=True)
            return

        column=view.Get_Column(x)
        column.reverse()
        for i in range(6):
            if column[i]==0:
                y=5-i
                break
        view.board[y][x]=value
        if y==0:
            for child in view.children:
                if isinstance(child,discord.ui.Select):
                    child.options=[option for option in child.options if option.value!=x]

        content=f'It is now {other_player}\'s turn.'
        message=view.Display_Board()

        winner=view.Winner_Check(view.player_1,view.player_2)
        if winner is not None:
            if winner==view.player_1:
                content=f'{interaction.guild.get_member(view.player_1).mention} won!'
            elif winner==view.player_2:
                content=f'{interaction.guild.get_member(view.player_2).mention} won!'
            else:
                content='It\'s a tie!'
            view.stop()
            view=None
        
        message+=f'\n{content}'
        await interaction.response.edit_message(content=message,view=view)

class Connect_4_Cog(commands.Cog):
    def __init__(self,bot:commands.bot):
        self.bot=bot
    
    class Connect_4_View(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.n=4
            self.board=[[0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0]]
            self.player_1=self.player_2=self.current_player=0
            self.add_item(Connect_4_Select_Menu())
        
        def Display_Board(self):
            message=''
            for row in self.board:
                for tile in row:
                    if tile==1:
                        message+='🔴'
                    elif tile==-1:
                        message+='🟡'
                    else:
                        message+='⬛'
                message+='\n'
            message+='1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n'
            return message

        def Get_Column(self,x):
            column=[]
            for row in self.board:
                column.append(row[x])
            return column
        
        def Winner_Check(self,player_1,player_2):
            n=self.n
            board=self.board
            rows=len(board)
            cols=len(board[0])
            for y in range(rows):
                for x in range(cols):
                    tile=board[y][x]
                    if tile==0:
                        continue
                    
                    #check row
                    value=0
                    if x+n<=cols:
                        for i in range(n):
                            value+=board[y][x+i]
                        if value==n:
                            return player_1
                        elif value==-n:
                            return player_2
                    
                    #check column
                    value=0
                    if y+n<=rows:
                        for i in range(n):
                            value+=board[y+i][x]
                        if value==n:
                            return player_1
                        elif value==-n:
                            return player_2

                    #check down-right diagonal
                    value=0
                    if x+n<=cols and y+n<=rows:
                        for i in range(n):
                            value+=board[y+i][x+i]
                        if value==n:
                            return player_1
                        elif value==-n:
                            return player_2
                    
                    #check down-left diagonal
                    value=0
                    if x-n+1>=0 and y+n<=rows:
                        for i in range(n):
                            value+=board[y+i][x-i]
                        if value==n:
                            return player_1
                        elif value==-n:
                            return player_2
            return None 

    @app_commands.command()
    async def connect4(self,interaction:discord.Interaction):
        board=[[0,0,0,0,0,0,0],
               [0,0,0,0,0,0,0],
               [0,0,0,0,0,0,0],
               [0,0,0,0,0,0,0],
               [0,0,0,0,0,0,0],
               [0,0,0,0,0,0,0]]
        message=''
        for y in range(6):
            for x in range(7):
                message+='⬛'
            message+='\n'
        message+='1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n'
        await interaction.response.send_message(message+'\nConnect 4: Red goes first',view=self.Connect_4_View())

 
async def setup(bot:commands.bot):
    await bot.add_cog(Connect_4_Cog(bot))