import discord
from discord import app_commands
from discord.ext import commands

from DataBase.Counting import Query, Update

class Counting_Cog(commands.Cog):
    def __init__(self,bot:commands.bot):
        self.bot=bot
    @app_commands.command()
    async def counting_info(self,interaction:discord.Interaction):
        await interaction.response.send_message(embed=discord.Embed(title="**Server Info**",description=f"Highscore: {Query(interaction.guild.id,'highscore')}\n\nCurrent Count: {Query(interaction.guild.id,'current_score')}\n\nCounting Channel: {interaction.guild.get_channel(Query(interaction.guild.id,'channel_id')).mention}",colour=0x00f8ff),ephemeral=True)
    @commands.Cog.listener('on_message')
    async def on_message(self,message:discord.Message):
        try:
            if Query(message.guild.id,'channel_id')==message.channel.id:
                if int(message.content)-1==Query(message.guild.id,'current_score'):
                    if message.author.id==Query(message.guild.id,'author_id') and not(Query(message.guild.id,'double_count')):
                        if Query(message.guild.id,'current_score')>Query(message.guild.id,'highscore'):
                            Update(message.guild.id,Query(message.guild.id,'current_score'),'highscore')
                        await message.channel.send(f"{message.author.mention} ruined the count at `{Query(message.guild.id,'current_score')}`! You can not double count. The next number is **`1`**")
                        await message.add_reaction("❌")
                        Update(message.guild.id,0,'current_score')
                    else:
                        await message.add_reaction("✅")
                        Update(message.guild.id,int(message.content),'current_score',message.id,message.author.id)
                else:
                    if Query(message.guild.id,'current_score')>Query(message.guild.id,'highscore'):
                        Update(message.guild.id,Query(message.guild.id,'current_score'),'highscore')
                    await message.channel.send(f"{message.author.mention} ruined the count at `{Query(message.guild.id,'current_score')}`! The next number is **`1`**")
                    await message.add_reaction("❌")
                    Update(message.guild.id,0,'current_score')
        except:
            return
    @commands.Cog.listener('on_message_delete')
    async def on_message_delete(self,message:discord.message):
        try:
            if message.id==Query(message.guild.id,'message_id'):
                await message.channel.send(f"{message.author.mention} deleted their count of `{Query(message.guild.id,'current_score')}`. The next number is **`{Query(message.guild.id,'current_score')+1}`**")
        except:
            return
async def setup(bot:commands.bot):
    await bot.add_cog(Counting_Cog(bot))