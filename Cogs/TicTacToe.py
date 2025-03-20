import discord, 
from discord import app_commands
from discord.ext import commands

import typing

# TicTacToe command
class TicTacToe_Cog(commands.Cog):
    def __init__(self,bot:commands.bot):
        self.bot=bot
    
    class TicTacToe(discord.ui.View):
        class TicTacToeButton(discord.ui.Button["discord.ui.View.TicTacToe"]):
            def __init__(self,x:int,y:int):
                super().__init__(style=discord.ButtonStyle.grey,label="\u200b",row=y)
                self.x=x
                self.y=y
            
            async def callback(self,interaction:discord.Interaction):
                view:view.TicTacToe=self.view #type:ignore
                if view.current_player==view.player_1==0:
                    view.player_1=view.current_player=interaction.user.id
                elif view.current_player==view.player_2==0:
                    if interaction.user.id==view.player_1:
                        await interaction.response.send_message(f"❌ {interaction.user.mention} you can not play against yourself.",ephemeral=True)
                        return
                    view.player_2=view.current_player=interaction.user.id
                if view.current_player==view.player_1==interaction.user.id:
                    self.style=discord.ButtonStyle.red
                    self.label="X"
                    self.disabled=True
                    view.board[self.y][self.x]=1
                    view.current_player=view.player_2
                    if view.player_2==0:
                        content="It is now Player 2's turn"
                    else:
                        content=f"It is now {interaction.guild.get_member(view.player_2).mention}'s turn."
                elif view.current_player==view.player_2==interaction.user.id:
                    self.style=discord.ButtonStyle.green
                    self.label="O"
                    self.disabled=True
                    view.board[self.y][self.x]=-1
                    view.current_player=view.player_1
                    content=f"It is now {interaction.guild.get_member(view.player_1).mention}'s turn."
                else:
                    if view.current_player==view.player_1 and view.player_2==interaction.user.id or view.current_player==view.player_2 and view.player_1==interaction.user.id:
                        message="❌ it is not your turn." 
                    else:
                        message="❌ this is not your game." 
                    await interaction.response.send_message(f"{interaction.user.mention} {message}",ephemeral=True)
                    return
                winner=view.Winner_Check(view.player_1,view.player_2)
                if winner is not None:
                    if winner==view.player_1:
                        content=f"{interaction.guild.get_member(view.player_1).mention} won!"
                    elif winner==view.player_2:
                        content=f"{interaction.guild.get_member(view.player_2).mention} won!"
                    else:
                        content="It's a tie!"
                    for child in view.children:
                        child.disabled=True
                    view.stop()
                await interaction.response.edit_message(content=content,view=view)
        
        children:typing.List[TicTacToeButton]
        
        def __init__(self):
            super().__init__()
            self.board=[[0,0,0],[0,0,0],[0,0,0]]
            self.player_1=self.player_2=self.current_player=0
            for x in range(3):
                for y in range(3):
                    self.add_item(self.TicTacToeButton(x,y))
        
        def Winner_Check(self,player_1,player_2):
            for row in self.board:
                value=sum(row)
                if value==3:
                    return player_1
                elif value==-3:
                    return player_2
            for i in range(3):
                value=self.board[0][i]+self.board[1][i]+self.board[2][i]
                if value==3:
                    return player_1
                elif value==-3:
                    return player_2
            diagonal=self.board[0][2]+self.board[1][1]+self.board[2][0]
            if diagonal==3:
                return player_1
            elif diagonal==-3:
                return player_2
            diagonal=self.board[0][0]+self.board[1][1]+self.board[2][2]
            if diagonal==3:
                return player_1
            elif diagonal==-3:
                return player_2
            if all(i!=0 for row in self.board for i in row):
                return 0
            return
    
    @app_commands.command()
    async def tictactoe(self,interaction:discord.Interaction):
        await interaction.response.send_message("Tic Tac Toe: X goes first",view=self.TicTacToe())


async def setup(bot:commands.bot):
    await bot.add_cog(TicTacToe_Cog(bot))