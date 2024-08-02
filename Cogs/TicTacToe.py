import discord, typing
from discord import app_commands
from discord.ext import commands

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
                if view.Current_player==view.Player_1==0:
                    view.Player_1=view.Current_player=interaction.user.id
                elif view.Current_player==view.Player_2==0:
                    if interaction.user.id==view.Player_1:
                        await interaction.response.send_message(f"❌ {interaction.user.mention} you can not play against yourself.",ephemeral=True)
                        return
                    view.Player_2=view.Current_player=interaction.user.id
                if view.Current_player==view.Player_1==interaction.user.id:
                    self.style=discord.ButtonStyle.red
                    self.label="X"
                    self.disabled=True
                    view.Board[self.y][self.x]=1
                    view.Current_player=view.Player_2
                    if view.Player_2==0:
                        Content="It is now Player 2's turn"
                    else:
                        Content=f"It is now {interaction.guild.get_member(view.Player_2).mention}'s turn."
                elif view.Current_player==view.Player_2==interaction.user.id:
                    self.style=discord.ButtonStyle.green
                    self.label="O"
                    self.disabled=True
                    view.Board[self.y][self.x]=-1
                    view.Current_player=view.Player_1
                    Content=f"It is now {interaction.guild.get_member(view.Player_1).mention}'s turn."
                else:
                    if view.Current_player==view.Player_1 and view.Player_2==interaction.user.id or view.Current_player==view.Player_2 and view.Player_1==interaction.user.id:
                        Message="❌ it is not your turn." 
                    else:
                        Message="❌ this is not your game." 
                    await interaction.response.send_message(f"{interaction.user.mention} {Message}",ephemeral=True)
                    return
                Winner=view.Winner_Check(view.Player_1,view.Player_2)
                if Winner is not None:
                    if Winner==view.Player_1:
                        Content=f"{interaction.guild.get_member(view.Player_1).mention} won!"
                    elif Winner==view.Player_2:
                        Content=f"{interaction.guild.get_member(view.Player_2).mention} won!"
                    else:
                        Content="It's a tie!"
                    for child in view.children:
                        child.disabled=True
                    view.stop()
                await interaction.response.edit_message(content=Content,view=view)
        children:typing.List[TicTacToeButton]
        def __init__(self):
            super().__init__()
            self.Board=[[0,0,0],[0,0,0],[0,0,0]]
            self.Player_1=self.Player_2=self.Current_player=0
            for x in range(3):
                for y in range(3):
                    self.add_item(self.TicTacToeButton(x,y))
        def Winner_Check(self,Player_1,Player_2):
            for Row in self.Board:
                Value=sum(Row)
                if Value==3:
                    return Player_1
                elif Value==-3:
                    return Player_2
            for i in range(3):
                Value=self.Board[0][i]+self.Board[1][i]+self.Board[2][i]
                if Value==3:
                    return Player_1
                elif Value==-3:
                    return Player_2
            Diagonal=self.Board[0][2]+self.Board[1][1]+self.Board[2][0]
            if Diagonal==3:
                return Player_1
            elif Diagonal==-3:
                return Player_2
            Diagonal=self.Board[0][0]+self.Board[1][1]+self.Board[2][2]
            if Diagonal==3:
                return Player_1
            elif Diagonal==-3:
                return Player_2
            if all(i!=0 for Row in self.Board for i in Row):
                return 0
            return
    @app_commands.command()
    async def tictactoe(self,interaction:discord.Interaction):
        await interaction.response.send_message("Tic Tac Toe: X goes first",view=self.TicTacToe())
async def setup(bot:commands.bot):
    await bot.add_cog(TicTacToe_Cog(bot))