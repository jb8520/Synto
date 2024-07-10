import mysql.connector, os

from dotenv import load_dotenv
load_dotenv()

def DataBase_Connection():
    return mysql.connector.connect(host=os.environ["DATABASE_HOST"],user=os.environ["DATABASE_USER"],password=os.environ["DATABASE_PASSWORD"],database=os.environ["DATABASE_NAME"])

def Update(Guild_id,Score,Query,Message_id=None,Author_id=None):
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute(f"UPDATE Counting SET {Query}='{Score}' WHERE guild_id='{Guild_id}'")
    Connection.commit()
    if Message_id is not None:
        Cursor.execute(f"UPDATE Counting SET message_id={Message_id} WHERE guild_id='{Guild_id}'")
        Connection.commit()
    else:
        Cursor.execute(f"UPDATE Counting SET message_id=0 WHERE guild_id='{Guild_id}'")
        Connection.commit()
    if Author_id is not None:
        Cursor.execute(f"UPDATE Counting SET author_id={Author_id} WHERE guild_id='{Guild_id}'")
        Connection.commit()
    else:
        Cursor.execute(f"UPDATE Counting SET Author_id=0 WHERE guild_id='{Guild_id}'")
        Connection.commit()
    Cursor.close()
    Connection.close()
def Query(Guild_id,Query,Connection=None):
    if Connection is None:
        Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute(f"SELECT {Query} FROM Counting WHERE guild_id='{Guild_id}'")
    Fetch=Cursor.fetchone()
    Connection.commit()
    Cursor.close()
    Connection.close()
    if Fetch is None:
        Configure(Guild_id,Configure=True)
        Cursor.execute(f"SELECT {Query} FROM Counting WHERE guild_id='{Guild_id}'")
        Fetch=Cursor.fetchone()
    if Query!="double_count":
        Fetch=int(Fetch[0])
        return Fetch
    else:
        if Fetch[0]=="True":
            return True
        elif Fetch[0]=="False":
            return False
def Configure(Guild_id,Channel_id=None,Double_Count=None,Configure=False,Connection=None):
    if Connection is None:
        Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    if Configure:
        Cursor.execute(f"INSERT INTO Counting (guild_id,channel_id,highscore,current_score,message_id,author_id,double_count) VALUES ('{Guild_id}','0','0','0','0','0','False')")
        Connection.commit()
    else:
        Cursor.execute(f"SELECT guild_id FROM Counting WHERE guild_id='{Guild_id}'")
        Fetch=Cursor.fetchone()
        if Fetch is None:
            Cursor.execute(f"INSERT INTO Counting (guild_id,channel_id,highscore,current_score,message_id,author_id,double_count) VALUES ('{Guild_id}','0','0','0','0','0','False')")
            Connection.commit()
    if Double_Count is not None:
        Cursor.execute(f"UPDATE Counting SET double_count='{Double_Count}' WHERE guild_id='{Guild_id}'")
    if Channel_id is not None:
        Cursor.execute(f"UPDATE Counting SET channel_id='{Channel_id}' WHERE guild_id='{Guild_id}'")
    Connection.commit()
    Cursor.close()
    Connection.close()
def Remove(Guild_id):
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute(f"DELETE FROM Counting WHERE guild_id='{Guild_id}'")
    Connection.commit()
    Cursor.close()
    Connection.close()