import discord

import Cogs.Setup as Setup
from DataBase.Economy import Configure, Query

class Economy_Settings_Menu_View(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Setup.Select_Menu())
    @discord.ui.button(label="Work",style=discord.ButtonStyle.grey)
    async def work(self,interaction:discord.Interaction,button:discord.ui.Button):
        View=Work_View()
        Configure(interaction.guild.id)
        Embed=discord.Embed(title="Work Settings ⚙️",colour=0x00F3FF)
        Embed.add_field(name="Cooldown",value=f"> {Query(interaction.guild.id,'work_cooldown')}")
        Embed.add_field(name="Payout Upper",value=f"> {Query(interaction.guild.id,'work_payout_upper')}")
        Embed.add_field(name="Payout Lower",value=f"> {Query(interaction.guild.id,'work_payout_lower')}")
        await interaction.response.send_message(embed=Embed,view=View)
    @discord.ui.button(label="Rob",style=discord.ButtonStyle.grey)
    async def rob(self,interaction:discord.Interaction,button:discord.ui.Button):
        View=Rob_View()
        Configure(interaction.guild.id)
        Embed=discord.Embed(title="Rob Settings ⚙️",colour=0x00F3FF)
        Embed.add_field(name="Cooldown",value=f"> {Query(interaction.guild.id,'rob_cooldown')}")
        Embed.add_field(name="Payout Upper",value=f"> {Query(interaction.guild.id,'rob_payout_upper')}")
        Embed.add_field(name="Payout Lower",value=f"> {Query(interaction.guild.id,'rob_payout_lower')}")
        Embed.add_field(name="Fine Upper",value=f"> {Query(interaction.guild.id,'rob_fine_upper')}")
        Embed.add_field(name="Fine Lower",value=f"> {Query(interaction.guild.id,'rob_fine_lower')}")
        Embed.add_field(name="Fail Percentage",value=f"> {Query(interaction.guild.id,'rob_percentage_fail')}")
        await interaction.response.send_message(embed=Embed,view=View)
    @discord.ui.button(label="Crime",style=discord.ButtonStyle.grey)
    async def crime(self,interaction:discord.Interaction,button:discord.ui.Button):
        View=Crime_View()
        Configure(interaction.guild.id)
        Embed=discord.Embed(title="Crime Settings ⚙️",colour=0x00F3FF)
        Embed.add_field(name="Cooldown",value=f"> {Query(interaction.guild.id,'crime_cooldown')}")
        Embed.add_field(name="Payout Upper",value=f"> {Query(interaction.guild.id,'crime_payout_upper')}")
        Embed.add_field(name="Payout Lower",value=f"> {Query(interaction.guild.id,'crime_payout_lower')}")
        Embed.add_field(name="Fine Upper",value=f"> {Query(interaction.guild.id,'crime_fine_upper')}")
        Embed.add_field(name="Fine Lower",value=f"> {Query(interaction.guild.id,'crime_fine_lower')}")
        Embed.add_field(name="Fail Percentage",value=f"> {Query(interaction.guild.id,'crime_percentage_fail')}")
        await interaction.response.send_message(embed=Embed,view=View)
    @discord.ui.button(label="Slots",style=discord.ButtonStyle.grey)
    async def slots(self,interaction:discord.Interaction,button:discord.ui.Button):
        View=Slots_View()
        Configure(interaction.guild.id)
        Embed=discord.Embed(title="Slots Settings ⚙️",colour=0x00F3FF)
        Embed.add_field(name="Jackpot Payout Multiplier",value=f"> {Query(interaction.guild.id,'slots_jackpot_payout_multiplier')}")
        Embed.add_field(name="Reward Payout Multiplier",value=f"> {Query(interaction.guild.id,'slots_reward_payout_multiplier')}")
        Embed.add_field(name="Minimum Bet",value=f"> {Query(interaction.guild.id,'slots_minimum_bet')}")
        await interaction.response.send_message(embed=Embed,view=View)
    @discord.ui.button(label="Blackjack",style=discord.ButtonStyle.grey)
    async def blackjack(self,interaction:discord.Interaction,button:discord.ui.Button):
        View=Blackjack_View()
        Configure(interaction.guild.id)
        Embed=discord.Embed(title="Blackjack Settings ⚙️",colour=0x00F3FF)
        Embed.add_field(name="Minimum Bet",value=f"> {Query(interaction.guild.id,'blackjack_minimum_bet')}")
        await interaction.response.send_message(embed=Embed,view=View)
    @discord.ui.button(label="delete",style=discord.ButtonStyle.red)
    async def delete(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        await interaction.message.delete()

class Input_Modal(discord.ui.Modal):
    def __init__(self,label,Column):
        super().__init__(title="placeholder")
        self.label=label
        self.Column=Column
    Input=discord.ui.TextInput(label="test",style=discord.TextStyle.short,required=True)
    async def on_submit(self,interaction:discord.Interaction):
        Configure(interaction.guild.id,Column=self.Column,Value=f"{self.Input}")
        await interaction.response.send_message(f"✅ Successfully set the {self.label} to {self.Input}",ephemeral=True)
        self.stop()

class Work_View(discord.ui.View):
    def __init__(self):
        super().__init__()
    def Embed(self,interaction):
        Embed=discord.Embed(title="Work Settings ⚙️",colour=0x00F3FF)
        Embed.add_field(name="Cooldown",value=f"> {Query(interaction.guild.id,'work_cooldown')}")
        Embed.add_field(name="Payout Upper",value=f"> {Query(interaction.guild.id,'work_payout_upper')}")
        Embed.add_field(name="Payout Lower",value=f"> {Query(interaction.guild.id,'work_payout_lower')}")
        return Embed
    @discord.ui.button(label="work_cooldown",style=discord.ButtonStyle.grey)
    async def work_cooldown(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="work_cooldown",Column="work_cooldown")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="work_payout_upper",style=discord.ButtonStyle.grey)
    async def work_payout_upper(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="work_payout_upper",Column="work_payout_upper")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="work_payout_lower",style=discord.ButtonStyle.grey)
    async def work_payout_lower(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="work_payout_lower",Column="work_payout_lower")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="delete",style=discord.ButtonStyle.red)
    async def delete(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        await interaction.message.delete()

class Rob_View(discord.ui.View):
    def __init__(self):
        super().__init__()
    def Embed(self,interaction):
        Embed=discord.Embed(title="Rob Settings ⚙️",colour=0x00F3FF)
        Embed.add_field(name="Cooldown",value=f"> {Query(interaction.guild.id,'rob_cooldown')}")
        Embed.add_field(name="Payout Upper",value=f"> {Query(interaction.guild.id,'rob_payout_upper')}")
        Embed.add_field(name="Payout Lower",value=f"> {Query(interaction.guild.id,'rob_payout_lower')}")
        Embed.add_field(name="Fine Upper",value=f"> {Query(interaction.guild.id,'rob_fine_upper')}")
        Embed.add_field(name="Fine Lower",value=f"> {Query(interaction.guild.id,'rob_fine_lower')}")
        Embed.add_field(name="Fail Percentage",value=f"> {Query(interaction.guild.id,'rob_percentage_fail')}")
        return Embed
    @discord.ui.button(label="rob_cooldown",style=discord.ButtonStyle.grey)
    async def rob_cooldown(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="rob_cooldown",Column="rob_cooldown")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="rob_payout_upper",style=discord.ButtonStyle.grey)
    async def rob_payout_upper(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="rob_payout_upper",Column="rob_payout_upper")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="rob_payout_lower",style=discord.ButtonStyle.grey)
    async def rob_payout_lower(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="rob_payout_lower",Column="rob_payout_lower")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="rob_fine_upper",style=discord.ButtonStyle.grey)
    async def rob_fine_upper(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="rob_fine_upper",Column="rob_fine_upper")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="rob_fine_lower",style=discord.ButtonStyle.grey)
    async def rob_fine_lower(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="rob_fine_lower",Column="rob_fine_lower")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="rob_percentage_fail",style=discord.ButtonStyle.grey)
    async def rob_percentage_fail(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="rob_percentage_fail",Column="rob_percentage_fail")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="delete",style=discord.ButtonStyle.red)
    async def delete(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        await interaction.message.delete()

class Crime_View(discord.ui.View):
    def __init__(self):
        super().__init__()
    def Embed(self,interaction):
        Embed=discord.Embed(title="Crime Settings ⚙️",colour=0x00F3FF)
        Embed.add_field(name="Cooldown",value=f"> {Query(interaction.guild.id,'crime_cooldown')}")
        Embed.add_field(name="Payout Upper",value=f"> {Query(interaction.guild.id,'crime_payout_upper')}")
        Embed.add_field(name="Payout Lower",value=f"> {Query(interaction.guild.id,'crime_payout_lower')}")
        Embed.add_field(name="Fine Upper",value=f"> {Query(interaction.guild.id,'crime_fine_upper')}")
        Embed.add_field(name="Fine Lower",value=f"> {Query(interaction.guild.id,'crime_fine_lower')}")
        Embed.add_field(name="Fail Percentage",value=f"> {Query(interaction.guild.id,'crime_percentage_fail')}")
        return Embed
    @discord.ui.button(label="crime_cooldown",style=discord.ButtonStyle.grey)
    async def crime_cooldown(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="crime_cooldown",Column="crime_cooldown")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="crime_payout_upper",style=discord.ButtonStyle.grey)
    async def crime_payout_upper(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="crime_payout_upper",Column="crime_payout_upper")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="crime_payout_lower",style=discord.ButtonStyle.grey)
    async def crime_payout_lower(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="crime_payout_lower",Column="crime_payout_lower")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="crime_fine_upper",style=discord.ButtonStyle.grey)
    async def crime_fine_upper(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="crime_fine_upper",Column="crime_fine_upper")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="crime_fine_lower",style=discord.ButtonStyle.grey)
    async def crime_fine_lower(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="crime_fine_lower",Column="crime_fine_lower")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="crime_percentage_fail",style=discord.ButtonStyle.grey)
    async def crime_percentage_fail(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="crime_percentage_fail",Column="crime_percentage_fail")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="delete",style=discord.ButtonStyle.red)
    async def delete(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        await interaction.message.delete()

class Slots_View(discord.ui.View):
    def __init__(self):
        super().__init__()
    def Embed(self,interaction):
        Embed=discord.Embed(title="Slots Settings ⚙️",colour=0x00F3FF)
        Embed.add_field(name="Jackpot Payout Multiplier",value=f"> {Query(interaction.guild.id,'slots_jackpot_payout_multiplier')}")
        Embed.add_field(name="Reward Payout Multiplier",value=f"> {Query(interaction.guild.id,'slots_reward_payout_multiplier')}")
        Embed.add_field(name="Minimum Bet",value=f"> {Query(interaction.guild.id,'slots_minimum_bet')}")
        return Embed
    @discord.ui.button(label="slots_jackpot_payout_multiplier",style=discord.ButtonStyle.grey)
    async def slots_jackpot_payout_multiplier(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="slots_jackpot_payout_multiplier",Column="slots_jackpot_payout_multiplier")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="slots_reward_payout_multiplier",style=discord.ButtonStyle.grey)
    async def slots_reward_payout_multiplier(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="slots_reward_payout_multiplier",Column="slots_reward_payout_multiplier")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="slots_minimum_bet",style=discord.ButtonStyle.grey)
    async def slots_minimum_bet(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="slots_minimum_bet",Column="slots_minimum_bet")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        await interaction.message.edit(embed=self.Embed(interaction))
    @discord.ui.button(label="delete",style=discord.ButtonStyle.red)
    async def delete(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        await interaction.message.delete()

class Blackjack_View(discord.ui.View):
    def __init__(self):
        super().__init__()
    @discord.ui.button(label="blackjack_minimum_bet",style=discord.ButtonStyle.grey)
    async def blackjack_minimum_bet(self,interaction:discord.Interaction,button:discord.ui.Button):
        Modal=Input_Modal(label="blackjack_minimum_bet",Column="blackjack_minimum_bet")
        await interaction.response.send_modal(Modal)
        await Modal.wait()
        Embed=discord.Embed(title="Blackjack Settings ⚙️",colour=0x00F3FF)
        Embed.add_field(name="Minimum Bet",value=f"> {Query(interaction.guild.id,'blackjack_minimum_bet')}")
        await interaction.message.edit(embed=Embed)
    @discord.ui.button(label="delete",style=discord.ButtonStyle.red)
    async def delete(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        await interaction.message.delete()