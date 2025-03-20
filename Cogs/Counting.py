import discord

from discord import app_commands
from discord.ext import commands

from DataBase.Counting import Query, Update

class Counting_Cog(commands.Cog):
    def __init__(self,bot:commands.bot):
        self.bot=bot
    
    # command which send stats about the counting in that server
    @app_commands.command()
    async def counting_stats(self,interaction:discord.Interaction):
        await interaction.response.send_message(embed=discord.Embed(title='**Server Stats**',description=f'Highscore: {Query(interaction.guild.id,'highscore')}\n\nCurrent Count: {Query(interaction.guild.id,'current_score')}\n\nCounting Channel: {interaction.guild.get_channel(Query(interaction.guild.id,'channel_id')).mention}',colour=0x00f8ff),ephemeral=True)
    
    # counting listners
    @commands.Cog.listener('on_message')
    async def on_message(self,message:discord.Message):
        try:
            counting_channel_id=Query(message.guild.id,'channel_id')
            current_score=Query(message.guild.id,'current_score')
            if counting_channel_id==message.channel.id:
                new_count=int(message.content)
                highscore=Query(message.guild.id,'highscore')
                if new_count==current_score+1:
                    last_counter_id=Query(message.guild.id,'author_id')
                    double_count=Query(message.guild.id,'double_count')
                    if message.author.id==last_counter_id and not(double_count):
                        if current_score>highscore:
                            Update(message.guild.id,current_score,'highscore')
                        await message.channel.send(f'{message.author.mention} ruined the count at `{current_score}`! You can\'t double count. The next number is **`1`**')
                        await message.add_reaction('❌')
                        Update(message.guild.id,0,'current_score')
                    else:
                        await message.add_reaction('✅')
                        Update(message.guild.id,new_count,'current_score',message.id,message.author.id)
                else:
                    if current_score>highscore:
                        Update(message.guild.id,current_score,'highscore')
                    await message.channel.send(f'{message.author.mention} ruined the count at `{current_score}`! The next number is **`1`**')
                    await message.add_reaction('❌')
                    Update(message.guild.id,0,'current_score')
        except:
            return
    
    @commands.Cog.listener('on_message_delete')
    async def on_message_delete(self,message:discord.message):
        try:
            current_message_id=Query(message.guild.id,'message_id')
            if message.id==current_message_id:
                current_score=Query(message.guild.id,'current_score')
                await message.channel.send(f'{message.author.mention} deleted their count of `{current_score}`. The next number is **`{current_score+1}`**')
        except:
            return


async def setup(bot:commands.bot):
    await bot.add_cog(Counting_Cog(bot))