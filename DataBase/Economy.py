import mysql.connector, os

from dotenv import load_dotenv
load_dotenv()

def DataBase_Connection():
    return mysql.connector.connect(host=os.environ["DATABASE_HOST"],user=os.environ["DATABASE_USER"],password=os.environ["DATABASE_PASSWORD"],database=os.environ["DATABASE_NAME"])

def Money_Query(Discord_id,Guild_id,Query):
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute(f"SELECT {Query} FROM Economy WHERE discord_id='{Discord_id}' and guild_id='{Guild_id}'")
    Fetch=Cursor.fetchone()
    Connection.commit()
    Cursor.close()
    Connection.close()
    if Fetch is None:
        return 0
    else:
        return int(Fetch[0])
def Update_Money(Discord_id,Guild_id,Query,Money):
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute(f"SELECT {Query} FROM Economy WHERE discord_id='{Discord_id}' and guild_id='{Guild_id}'")
    Fetch=Cursor.fetchone()
    if Fetch is None:
        Cursor.execute(f"INSERT INTO Economy (discord_id,guild_id,money,bank,total) VALUES ('{Discord_id}','{Guild_id}','{Money}','0','{Money}')")
    else:
        Money+=int(Fetch[0])
        Cursor.execute(f"UPDATE Economy SET {Query}='{Money}' WHERE discord_id='{Discord_id}' and guild_id='{Guild_id}'")
    Connection.commit()
    Cursor.close()
    Connection.close()
    Update_Total(Discord_id,Guild_id)
def Update_Total(Discord_id,Guild_id):
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute(f"SELECT total FROM Economy WHERE discord_id='{Discord_id}' and guild_id='{Guild_id}'")
    Total=Cursor.fetchone()
    Cursor.execute(f"SELECT bank FROM Economy WHERE discord_id='{Discord_id}' and guild_id='{Guild_id}'")
    Bank=Cursor.fetchone()
    Cursor.execute(f"SELECT money FROM Economy WHERE discord_id='{Discord_id}' and guild_id='{Guild_id}'")
    Money=Cursor.fetchone()
    if int(Bank[0])+int(Money[0])!=int(Total[0]):
        Cursor.execute(f"UPDATE Economy SET total='{int(Bank[0])+int(Money[0])}' WHERE discord_id='{Discord_id}' and guild_id='{Guild_id}'")
    Connection.commit()
    Cursor.close()
    Connection.close()
def Leaderboard_Query(Discord_id,Guild_id,Query):
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute(f"SELECT {Query} FROM Economy WHERE guild_id='{Guild_id}'")
    Leaderboard=Cursor.fetchall()
    if len(Leaderboard)>10:
        Leaderboard=Leaderboard[:10]
    List=[]
    for i in range(len(Leaderboard)):
        List.append(int(Leaderboard[i][0]))
    List.sort(reverse=True)
    Leaderboard=[]
    for i in List:
        Cursor.execute(f"SELECT discord_id,{Query} FROM Economy WHERE {Query}='{i}' and guild_id='{Guild_id}'")
        Leaderboard.append(Cursor.fetchone())
    Cursor.execute(f"SELECT {Query} FROM Economy WHERE discord_id='{Discord_id}' and guild_id='{Guild_id}'")
    User_Money=Cursor.fetchone()
    Cursor.close()
    Connection.close()
    return Leaderboard,User_Money

def Query(Guild_id,Query):
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute(f"SELECT {Query} FROM Economy_Settings WHERE guild_id='{Guild_id}'")
    Fetch=Cursor.fetchone()[0]
    Cursor.close()
    Connection.close()
    return int(Fetch)

def Configure(Guild_id,Column=None,Value=None):
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute(f"SELECT guild_id FROM Economy_Settings WHERE guild_id='{Guild_id}'")
    Fetch=Cursor.fetchone()
    if Fetch is None:
        Cursor.execute(f"INSERT INTO Economy_Settings (guild_id,work_cooldown,work_payout_upper,work_payout_lower,rob_cooldown,rob_payout_upper,rob_payout_lower,rob_fine_upper,rob_fine_lower,rob_percentage_fail,crime_cooldown,crime_payout_upper,crime_payout_lower,crime_fine_upper,crime_fine_lower,crime_percentage_fail,slots_jackpot_payout_multiplier,slots_reward_payout_multiplier,slots_minimum_bet,blackjack_minimum_bet) VALUES ('{Guild_id}',60,50,10,10800,0.5,0.1,300,100,0.3,10800,700,250,0.4,0.1,0.3,50,5,100,100)")
        Connection.commit()
    if Column is not None and Value is not None:
        Cursor.execute(f"UPDATE Economy_Settings SET {Column}='{Value}' WHERE guild_id='{Guild_id}'")
        Connection.commit()
    Cursor.close()
    Connection.close()