import discord, random
from discord import app_commands
from discord.ext import commands

from DataBase.Economy import Update_Money, Money_Query, Leaderboard_Query, Query

class Economy_Cog(commands.Cog):
    def __init__(self,bot:commands.bot):
        self.bot=bot
    @app_commands.command()
    async def give(self,interaction:discord.Interaction,user:discord.User=None,amount:int=None):
        if amount<=0:
            await interaction.response.send_message(f"❌ You can not give 🪙{amount}.",ephemeral=True)
            return
        elif amount>Money_Query(interaction.user.id,interaction.guild.id,'money'):
            await interaction.response.send_message(f"❌ You do not have 🪙{amount} in cash.",ephemeral=True)
            return
        Update_Money(interaction.user.id,interaction.guild.id,"money",-amount)
        Update_Money(user.id,interaction.guild.id,"money",amount)
    @app_commands.command()
    @app_commands.choices(order=[app_commands.Choice(name="Total",value="total"),app_commands.Choice(name="Bank",value="bank"),app_commands.Choice(name="Cash",value="money")])
    async def leaderboard(self,interaction:discord.Interaction,order:app_commands.Choice[str]=None):
        if order is None:
            name="Total"
            value="total"
        else:
            name=order.name
            value=order.value
        Leaderboard=Leaderboard_Query(interaction.user.id,interaction.guild.id,value)
        Top_Ten=""
        for i in range(len(Leaderboard[0])):
            try:
                Top_Ten+=f"{i+1}. {interaction.guild.get_member(int(Leaderboard[0][i][0])).mention} • 🪙{Leaderboard[0][i][1]}\n"
            except:
                Top_Ten+=f"{i+1}. {(Leaderboard[0][i][0])} • 🪙{Leaderboard[0][i][1]}\n"
        await interaction.response.send_message(embed=discord.Embed(description=f"**Leaderboard**\n\n{Top_Ten}\nYour {name}: 🪙{Leaderboard[1][0]}",colour=0x00f8ff).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar))
    @app_commands.command()
    async def balance(self,interaction:discord.Interaction,user:discord.User=None):
        if user is None:
            user=interaction.user
        Cash=Money_Query(user.id,interaction.guild.id,'money')
        Bank=Money_Query(user.id,interaction.guild.id,'bank')
        await interaction.response.send_message(embed=discord.Embed(description=f"**Cash:** 🪙{Cash}\n\n**Bank:** 🪙{Bank}\n\n**Total:** 🪙{Cash+Bank}\n\nUse the `leaderboard` command to view your rank.",colour=0x00f8ff).set_author(name=str(user),icon_url=user.display_avatar))
    @app_commands.command()
    async def deposit(self,interaction:discord.Interaction,amount:str="all"):
        if amount.lower()!="all":
            try:
                amount=int(amount)
            except:
                await interaction.response.send_message(f"❌ The amount `{amount}` is not a valid number of coins.",ephemeral=True)
                return
        else:
            amount=Money_Query(interaction.user.id,interaction.guild.id,'money')
        if type(amount)==int:
            if amount<=0:
                await interaction.response.send_message(f"❌ You can not deposit 🪙{amount}.",ephemeral=True)
                return
            elif amount>Money_Query(interaction.user.id,interaction.guild.id,'money'):
                await interaction.response.send_message(f"❌ You do not have 🪙{amount} in cash.",ephemeral=True)
                return
        Update_Money(interaction.user.id,interaction.guild.id,"money",-amount)
        Update_Money(interaction.user.id,interaction.guild.id,"bank",amount)
        await interaction.response.send_message(embed=discord.Embed(description=f"✅ Deposited 🪙{amount} to your bank!",colour=0x00f8ff).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar))
    @app_commands.command()
    async def withdraw(self,interaction:discord.Interaction,amount:str="all"):
        if amount.lower()!="all":
            try:
                amount=int(amount)
            except:
                await interaction.response.send_message(f"❌ The amount `{amount}` is not a valid number of coins.",ephemeral=True)
                return
        else:
            amount=Money_Query(interaction.user.id,interaction.guild.id,'bank')
        if type(amount)==int:
            if amount<=0:
                await interaction.response.send_message(f"❌ You can not withdraw 🪙{amount}.",ephemeral=True)
                return
            elif amount>Money_Query(interaction.user.id,interaction.guild.id,'bank'):
                await interaction.response.send_message(f"❌ You do not have 🪙{amount} in your bank.",ephemeral=True)
                return
        Update_Money(interaction.user.id,interaction.guild.id,"money",amount)
        Update_Money(interaction.user.id,interaction.guild.id,"bank",-amount)
        await interaction.response.send_message(embed=discord.Embed(description=f"✅ Withdrew 🪙{amount} from your bank!",colour=0x00f8ff).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar))
    def Cooldown(interaction:discord.Interaction):
        return app_commands.Cooldown(1,Query(interaction.guild.id,f"{interaction.command.name}_cooldown"))
    @app_commands.command()
    @app_commands.checks.dynamic_cooldown(Cooldown)
    async def work(self,interaction:discord.Interaction):
        Money=random.randint(Query(interaction.guild.id,"work_payout_lower"),Query(interaction.guild.id,"work_payout_upper"))
        Update_Money(interaction.user.id,interaction.guild.id,"money",Money)
        await interaction.response.send_message(embed=discord.Embed(description=f"You earnt 🪙{Money} working.",colour=0x00ff12).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar))
    @app_commands.command()
    @app_commands.checks.dynamic_cooldown(Cooldown)
    async def rob(self,interaction:discord.Interaction,user:discord.User):
        if user==interaction.user:
            await interaction.response.send_message(embed=discord.Embed(description=f"{user.mention} you can not rob yourself!",colour=0xff0000).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar),ephemeral=True)
        elif Money_Query(user.id,interaction.guild.id,"money")==0 or Money_Query(user.id,interaction.guild.id,"money")<0:
            await interaction.response.send_message(embed=discord.Embed(description=f"{user.mention} had no money to be stolen!",colour=0xff0000).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar),ephemeral=True)
            return
        else:
            if random.randint(0,1)> Query(interaction.guild.id,"rob_fail_percentage"):
                Percentage_Payout=random.randint(Query(interaction.guild.id,"rob_payout_lower"),Query(interaction.guild.id,"rob_payout_upper"))
                User_Cash=Money_Query(user.id,interaction.guild.id,"money")
                Update_Money(interaction.user.id,interaction.guild.id,"money",Percentage_Payout*User_Cash)
                Update_Money(user.id,interaction.guild.id,"money",-Percentage_Payout*User_Cash)
                await interaction.response.send_message(embed=discord.Embed(description=f"You robbed 🪙{Percentage_Payout*User_Cash} from {str(user)}.",colour=0x00ff12).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar))
            else:
                Fine=random.randint(Query(interaction.guild.id,"rob_fine_lower"),Query(interaction.guild.id,"rob_fine_upper"))
                Update_Money(interaction.user.id,interaction.guild.id,"money",-Fine)
                await interaction.response.send_message(embed=discord.Embed(description=f"❌ You were caught while trying to rob {str(user)}. You are fined 🪙{Fine}!",colour=0xff0000).set_author(name=str(interaction.user),icon_url=interaction.user.display_avatar))
    async def cog_app_command_error(self,interaction:discord.Interaction,error:discord.app_commands.AppCommandError):
        if isinstance(error,discord.app_commands.errors.CommandOnCooldown):
            Timer=int(round(error.retry_after,0))
            Time_Unit="seconds"
            if Timer>=3600:
                Timer=int(round((error.retry_after/3600),0))
                Time_Unit="hours"
            elif Timer>=60:
                Timer=int(round((error.retry_after/60),0))
                Time_Unit="minutes"
            await interaction.response.send_message(f"❌ The command `{interaction.command.name}` is on cooldown, you can use it again in `{Timer} {Time_Unit}`.",ephemeral=True)
        else:
            print(error)
async def setup(bot:commands.bot):
    await bot.add_cog(Economy_Cog(bot))