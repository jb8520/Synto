import discord, random
from discord import app_commands
from discord.ext import commands

from DataBase.Economy import Update_Money, Money_Query, Query

class Casino_Cog(commands.Cog):
    def __init__(self,bot:commands.bot):
        self.bot=bot
    @app_commands.command()
    async def slot(self,interaction:discord.Interaction,bet:int=None):
        if bet is None:
            bet=Query(interaction.guild.id,'slots_minimum_bet')
        elif not bet>=Query(interaction.guild.id,'slots_minimum_bet'):
            await interaction.response.send_message(f"❌ The minimum bet is {Query(interaction.guild.id,'slots_minimum_bet')}.",ephemeral=True)
            return
        if bet>Money_Query(interaction.user.id,interaction.guild.id,'money'):
            await interaction.response.send_message(f"❌ You do not have that much money.",ephemeral=True)
            return
        Reels=[]
        for i in range(4):
            Reels.append(random.choice(["♥️","♦️","♠️","♣️"]))
        Colour=0x00ff12
        if Reels[0]==Reels[1]==Reels[2]==Reels[3]:
            Update_Money(interaction.user.id,interaction.guild.id,"money",Query(interaction.guild.id,'slots_jackpot_payout_multiplier')*bet)
            Result=f"You got the jackpot! 🪙{Query(interaction.guild.id,'slots_jackpot_payout_multiplier')*bet}"
        elif Reels[0]==Reels[1]==Reels[2] or Reels[0]==Reels[1]==Reels[3] or Reels[0]==Reels[2]==Reels[3] or Reels[1]==Reels[2]==Reels[3]:
            Update_Money(interaction.user.id,interaction.guild.id,"money",Query(interaction.guild.id,'slots_reward_payout_multiplier')*bet)
            Result=f"You got three of a kind! 🪙{Query(interaction.guild.id,'slots_reward_payout_multiplier')*bet}"
        else:
            Update_Money(interaction.user.id,interaction.guild.id,"money",-bet)
            Result=f"You lost 🪙-{bet}"
            Colour=0xff0000
        await interaction.response.send_message(embed=discord.Embed(description=f"{Reels[0]} {Reels[1]} {Reels[2]} {Reels[3]}\n\n{Result}",colour=Colour).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar))
    @app_commands.command()
    async def blackjack(self,interaction:discord.Interaction,bet:int=None):
        if bet is None:
            bet=Query(interaction.guild.id,'blackjack_minimum_bet')
        elif not bet>=Query(interaction.guild.id,'blackjack_minimum_bet'):
            await interaction.response.send_message(f"❌ The minimum bet is {Query(interaction.guild.id,'blackjack_minimum_bet')}.",ephemeral=True)
            return
        if bet>Money_Query(interaction.user.id,interaction.guild.id,'money'):
            await interaction.response.send_message(f"❌ You do not have that much money.",ephemeral=True)
            return
        Deck=["<:AC:1048683525706100827>","<:2C:1048683514129821717>","<:3C:1048683515530711131>","<:4C:1048683516793196584>","<:5C:1048683518110208060>","<:6C:1048683507251150889>","<:7C:1048683508387823727>","<:8C:1048683509490917397>","<:9C:1048683511013441646>","<:10C:1048683512544366693>","<:JC:1048683526754668655>","<:QC:1048683528818266262>","<:KC:1048683544119091252>","<:AS:1048952051754860604>","<:2S:1048951956913279027>","<:3S:1048951958326743051>","<:4S:1048951960285491261>","<:5S:1048951961711554582>","<:6S:1048951962705604659>","<:7S:1048951964161019904>","<:8S:1048951965478043659>","<:9S:1048951966790848603>","<:10S:1048951968007192649>","<:JS:1048952049057923102>","<:QS:1048951971903713370>","<:KS:1048952050542710814>","<:AD:1048951757625118780>","<:2D:1048951741892268153>","<:3D:1048951743842619442>","<:4D:1048951745012834314>","<:5D:1048951746334044190>","<:6D:1048951747869167676>","<:7D:1048951749530103929>","<:8D:1048951753766350879>","<:9D:1048951755074969628>","<:10D:1048951756396183582>","<:JD:1048951836507385926>","<:QD:1048951837883109407>","<:KD:1048951759730655262>","<:AH:1048951621104701510>","<:2H:1048951672782737478>","<:3H:1048951665472045146>","<:4H:1048951666600321095>","<:5H:1048951667871199313>","<:6H:1048951669209182268>","<:7H:1048951670396178442>","<:8H:1048951671490887680>","<:9H:1048951699718537226>","<:10H:1048951700951683112>","<:JH:1048951622312661033>","<:QH:1048951624485306448>","<:KH:1048951623348666428>"]
        Partial_Dealer_Hand=[]
        User_Hand=self.Deal_Hand(Deck)
        Dealer_Hand=self.Deal_Hand(Deck)
        if Total_Value(User_Hand)==Total_Value(Dealer_Hand)==21:
            await interaction.response.send_message(embed=discord.Embed(description=f"**Result:** Draw \n\n**Your hand:** {self.Card_View(User_Hand,Partial_Dealer_Hand)}\nValue: {Total_Value(User_Hand)}\n\n**Dealer Hand:** {Card_View(Dealer_Hand,Partial_Dealer_Hand)}\nValue: {Total_Value(Dealer_Hand)}",colour=0xff9200).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar))
        elif Total_Value(User_Hand)==21:
            Update_Money(interaction.user.id,interaction.guild.id,"money",bet)
            await interaction.response.send_message(embed=discord.Embed(description=f"**Result:** Win 🪙{bet}\n\n**Your hand:** {Card_View(User_Hand,Partial_Dealer_Hand)}\nValue: {Total_Value(User_Hand)}\n\n**Dealer Hand:** {Card_View(Dealer_Hand,Partial_Dealer_Hand)}\nValue: {Total_Value(Dealer_Hand)}",colour=0x00ff12).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar))
        elif Total_Value(Dealer_Hand)==21:
            Update_Money(interaction.user.id,interaction.guild.id,"money",-bet)
            await interaction.response.send_message(embed=discord.Embed(description=f"**Result:** Loss 🪙-{bet}\n\n**Your hand:** {Card_View(User_Hand,Partial_Dealer_Hand)}\nValue: {Total_Value(User_Hand)}\n\n**Dealer Hand:** {Card_View(Dealer_Hand,Partial_Dealer_Hand)}\nValue: {Total_Value(Dealer_Hand)}",colour=0xff0000).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar))
        else:
            Partial_Dealer_Hand.append(Dealer_Hand[0])
            await interaction.response.send_message(embed=discord.Embed(description=f"**Your hand:** {Card_View(User_Hand,Partial_Dealer_Hand)}\nValue: {Total_Value(User_Hand)}\n\n**Dealer Hand:** {Card_View(Partial_Dealer_Hand,Partial_Dealer_Hand)}\nValue: {Total_Value(Partial_Dealer_Hand)}",colour=0x00f8ff).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar),view=self.BlackJack_Game_Buttons(User=interaction.user,Bet=bet,Deck=Deck,User_Hand=User_Hand,Dealer_Hand=Dealer_Hand,Partial_Dealer_Hand=Partial_Dealer_Hand))
    def Deal_Hand(self,Deck):
        Hand=[]
        for i in range(2):
            random.shuffle(Deck)
            Hand.append(Deck.pop())
        return Hand 
    class BlackJack_Game_Buttons(discord.ui.View):
        def __init__(self,*,User,Bet,Deck,User_Hand,Dealer_Hand,Partial_Dealer_Hand):
            super().__init__(timeout=None)
            self.User=User
            self.Bet=Bet
            self.Deck=Deck
            self.User_Hand=User_Hand
            self.Dealer_Hand=Dealer_Hand
            self.Partial_Dealer_Hand=Partial_Dealer_Hand
        @discord.ui.button(label="Hit",style=discord.ButtonStyle.blurple)
        async def Hit(self,interaction:discord.Interaction,button:discord.ui.Button):
            if interaction.user!=self.User:
                await interaction.response.send_message(f"❌ {interaction.user.mention} this is not your game session.",ephemeral=True)
            await interaction.response.defer()
            self.Hit_Function(self.User_Hand,self.Deck)
            if Total_Value(self.User_Hand)>21:
                Update_Money(interaction.user.id,interaction.guild.id,"money",-self.Bet)
                await interaction.message.edit(embed=discord.Embed(description=f"**Result:** Bust 🪙-{self.Bet}\n\n**Your hand:** {Card_View(self.User_Hand,self.Partial_Dealer_Hand)}\nValue: {Total_Value(self.User_Hand)}\n\n**Dealer Hand:** {Card_View(self.Dealer_Hand,self.Partial_Dealer_Hand)}\nValue: {Total_Value(self.Dealer_Hand)}",colour=0xff0000).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar),view=None)
            elif Total_Value(self.User_Hand)==21:
                Update_Money(interaction.user.id,interaction.guild.id,"money",self.Bet)
                await interaction.message.edit(embed=discord.Embed(description=f"**Result:** Win 🪙{self.Bet}\n\n**Your hand:** {Card_View(self.User_Hand,self.Partial_Dealer_Hand)}\nValue: {Total_Value(self.User_Hand)}\n\n**Dealer Hand:** {Card_View(self.Dealer_Hand,self.Partial_Dealer_Hand)}\nValue: {Total_Value(self.Dealer_Hand)}",colour=0x00ff12).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar),view=None)
            else:
                await interaction.message.edit(embed=discord.Embed(description=f"**Your hand:** {Card_View(self.User_Hand,self.Partial_Dealer_Hand)}\nValue: {Total_Value(self.User_Hand)}\n\n**Dealer Hand:** {Card_View(self.Partial_Dealer_Hand,self.Partial_Dealer_Hand)}\nValue: {Total_Value(self.Partial_Dealer_Hand)}",colour=0x00f8ff).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar))    
        @discord.ui.button(label="Stand",style=discord.ButtonStyle.green)
        async def Stand(self,interaction:discord.Interaction,button:discord.ui.Button):
            if interaction.user!=self.User:
                await interaction.response.send_message(f"❌ {interaction.user.mention} this is not your game session.",ephemeral=True)
                return
            await interaction.response.defer()
            while Total_Value(self.Dealer_Hand)<17:
                self.Hit_Function(self.Dealer_Hand,self.Deck)
                if Total_Value(self.Dealer_Hand)>21:
                    Update_Money(interaction.user.id,interaction.guild.id,"money",self.Bet)
                    await interaction.message.edit(embed=discord.Embed(description=f"**Result:** Dealer Bust 🪙{self.Bet}\n\n**Your hand:** {Card_View(self.User_Hand,self.Partial_Dealer_Hand)}\nValue: {Total_Value(self.User_Hand)}\n\n**Dealer Hand:** {Card_View(self.Dealer_Hand,self.Partial_Dealer_Hand)}\nValue: {Total_Value(self.Dealer_Hand)}",colour=0x00ff12).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar),view=None)
                    return
            Result=self.Score(self.Bet,self.User_Hand,self.Dealer_Hand,interaction.user.id,interaction.guild.id)
            await interaction.message.edit(embed=discord.Embed(description=f"**Result:** {Result[0]}\n\n**Your hand:** {Card_View(self.User_Hand,self.Partial_Dealer_Hand)}\nValue: {Total_Value(self.User_Hand)}\n\n**Dealer Hand:** {Card_View(self.Dealer_Hand,self.Partial_Dealer_Hand)}\nValue: {Total_Value(self.Dealer_Hand)}",colour=Result[1]).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar),view=None)
        @discord.ui.button(label="Cancel",style=discord.ButtonStyle.red)
        async def Cancel(self,interaction:discord.Interaction,button:discord.ui.Button):
            if interaction.user!=self.User:
                await interaction.response.send_message(f"❌ {interaction.user.mention} this is not your game session.",ephemeral=True)
                return
            await interaction.response.defer()
            Update_Money(interaction.user.id,interaction.guild.id,"money",-100)
            self.stop()
            await interaction.message.edit(embed=discord.Embed(description="The game session was cancelled.",colour=0x00f8ff).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar),view=None)
        def Hit_Function(self,Hand,Deck):
            Card=Deck.pop()
            Hand.append(Card)
            return Hand
        def Score(self,Bet,User_Hand,Dealer_Hand,User_id,Guild_id):
            if Total_Value(User_Hand)==Total_Value(Dealer_Hand):
                Result="Draw"
                Colour=0xff9200
            elif Total_Value(User_Hand)==21:
                Update_Money(User_id,Guild_id,"money",Bet)
                Result=f"Win 🪙{Bet}"
                Colour=0x00ff12
            elif Total_Value(Dealer_Hand)==21:
                Update_Money(User_id,Guild_id,"money",-Bet)
                Result=f"Loss 🪙-{Bet}"
                Colour=0xff0000
            elif Total_Value(User_Hand)>21:
                Update_Money(User_id,Guild_id,"money",-Bet)
                Result=f"Bust 🪙-{Bet}"
                Colour=0xff0000
            elif Total_Value(Dealer_Hand)>21:
                Update_Money(User_id,Guild_id,"money",Bet)
                Result=f"Dealer bust 🪙{Bet}"
                Colour=0x00ff12
            elif Total_Value(User_Hand)<Total_Value(Dealer_Hand):
                Update_Money(User_id,Guild_id,"money",-Bet)
                Result=f"Loss 🪙-{Bet}"
                Colour=0xff0000
            elif Total_Value(User_Hand)>Total_Value(Dealer_Hand):
                Update_Money(User_id,Guild_id,"money",Bet)
                Result=f"Win 🪙{Bet}"
                Colour=0x00ff12
            return Result,Colour
def Total_Value(Hand):
    Total=0
    for Card in Hand:
        if Card[3:4]!="0":
            Card=Card[2:3]
        else:
            Card=Card[2:4]
        if Card=="J" or Card=="Q" or Card=="K":
            Total+=10
        elif Card=="A":
            if Total>=11:
                Total+=1
            else:
                Total+=11
        else:
            Total+=int(Card)
    return Total
def Card_View(Hand,Partial_Dealer_Hand):
    Cards=""
    for Card in Hand:
        Cards=Cards+Card
    if Hand==Partial_Dealer_Hand:
        Cards=Cards+"<:Blank:1048948096886919248>"
    return Cards
async def setup(bot:commands.bot):
    await bot.add_cog(Casino_Cog(bot))