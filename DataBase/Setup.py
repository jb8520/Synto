import mysql.connector, os

from dotenv import load_dotenv
load_dotenv()

def DataBase_Connection():
    return mysql.connector.connect(host=os.environ["DATABASE_HOST"],user=os.environ["DATABASE_USER"],password=os.environ["DATABASE_PASSWORD"],database=os.environ["DATABASE_NAME"])

def Add_Auto_Vc_Table():
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute("CREATE TABLE IF NOT EXISTS Auto_Vc(guild_id text NOT NULL, vc_creator_id text, vc_category_id text, member_role text, bypass_roles text)")
    Connection.commit()
    Cursor.close()
    Connection.close()
def Add_Counting_Table():
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute("CREATE TABLE IF NOT EXISTS Counting(guild_id text NOT NULL, channel_id text NOT NULL, highscore text NOT NULL, current_score text NOT NULL, message_id text, author_id text, double_count text not Null)")
    Connection.commit()
    Cursor.close()
    Connection.close()
def Add_Economy_Table():
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute("CREATE TABLE IF NOT EXISTS Economy(discord_id text NOT NULL, guild_id text NOT NULL, money text NOT NULL, bank text NOT NULL, total text NOT NULL)")
    Connection.commit()
    Cursor.close()
    Connection.close()
def Add_Economy_Settings_Table():
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute("CREATE TABLE IF NOT EXISTS Economy_Settings(guild_id text NOT NULL, work_cooldown text NOT NULL, work_payout_upper text NOT NULL, work_payout_lower text NOT NULL, rob_cooldown text NOT NULL, rob_payout_upper text NOT NULL, rob_payout_lower text NOT NULL, rob_fine_upper text NOT NULL, rob_fine_lower text NOT NULL, rob_percentage_fail text NOT NULL, crime_cooldown text NOT NULL, crime_payout_upper text NOT NULL, crime_payout_lower text NOT NULL, crime_fine_upper text NOT NULL, crime_fine_lower text NOT NULL, crime_percentage_fail text NOT NULL, slots_jackpot_payout_multiplier text NOT NULL, slots_reward_payout_multiplier text NOT NULL, slots_minimum_bet text NOT NULL, blackjack_minimum_bet text NOT NULL)")
    Connection.commit()
    Cursor.close()
    Connection.close()
def Add_Welcome_Message_Table():
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute("CREATE TABLE IF NOT EXISTS Welcome_Message(guild_id text NOT NULL, channel_id text NOT NULL, title text NOT NULL, description text NOT NULL, colour text NOT NULL, activated text NOT NULL)")
    Connection.commit()
    Cursor.close()
    Connection.close()
# Add_Auto_Vc_Table()
# Add_Counting_Table()
# Add_Economy_Table()
# Add_Economy_Settings_Table()
# Add_Welcome_Message_Table()