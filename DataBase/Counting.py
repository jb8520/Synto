import mysql.connector, os

from dotenv import load_dotenv
load_dotenv()

def DataBase_Connection():
    return mysql.connector.connect(host=os.environ["DATABASE_HOST"],user=os.environ["DATABASE_USER"],password=os.environ["DATABASE_PASSWORD"],database=os.environ["DATABASE_NAME"])


def Counting_Channel_Query(guild_id):
    connection=DataBase_Connection()
    cursor=connection.cursor()
    cursor.execute(f"SELECT channel_id FROM Counting WHERE guild_id='{guild_id}'")
    fetch=cursor.fetchone()
    connection.close()
    if fetch is None:
        Add_Server(guild_id,connection,cursor)
        fetch=[0]
    connection.close()
    cursor.close()
    vc_creator_id=int(fetch[0])
    if vc_creator_id==0:
        return vc_creator_id,'❌ The counting channel is not set to a valid channel'
    else:
        return vc_creator_id,'✅ Success!'

def Double_Count_Query(guild_id):
    connection=DataBase_Connection()
    cursor=connection.cursor()
    cursor.execute(f"SELECT double_count FROM Auto_Vc WHERE guild_id='{guild_id}'")
    fetch=cursor.fetchone()
    connection.close()
    if fetch is None:
        Add_Server(guild_id,connection,cursor)
        fetch=['False']
    connection.close()
    cursor.close()
    vc_creator_id=bool(fetch[0])
    if vc_creator_id==0:
        return vc_creator_id,'❌ Double count is not set to a correct option'
    else:
        return vc_creator_id,'✅ Success!'



def Add_Server(guild_id,connection=DataBase_Connection(),cursor=None):
    if cursor is None:
        cursor=connection.cursor()
    cursor.execute(f"INSERT INTO Counting (guild_id,channel_id,highscore,current_score,message_id,author_id,double_count) VALUES ('{guild_id}','0','0','0','0','0','False')")
    connection.commit()

def Remove_Server(guild_id):
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute(f"DELETE FROM Counting WHERE guild_id='{guild_id}'")
    Connection.commit()
    Cursor.close()
    Connection.close()


def Query(guild_id):
    connection=DataBase_Connection()
    cursor=connection.cursor()
    cursor.execute(f"SELECT * FROM Counting WHERE guild_id='{guild_id}'")
    fetch=cursor.fetchone()
    if fetch is None:
        Add_Server(guild_id,connection,cursor)
        fetch=(guild_id,0,0,0,0,0,False)
    guild_id,channel_id,highscore,current_score,message_id,author_id,double_count=fetch
    channel_id=int(channel_id)
    highscore=int(highscore)
    current_score=int(current_score)
    message_id=int(message_id)
    author_id=int(author_id)
    double_count=bool(double_count)
    return channel_id,highscore,current_score,message_id,author_id,double_count


def Configure(guild_id,channel_id=None,double_count=None):
    connection=DataBase_Connection()
    cursor=connection.cursor()
    cursor.execute(f"SELECT guild_id FROM Counting WHERE guild_id='{guild_id}'")
    Fetch=cursor.fetchone()
    if Fetch is None:
        Add_Server(guild_id,connection,cursor)
    updated=False
    if channel_id is not None:
        cursor.execute(f"UPDATE Counting SET channel_id='{channel_id}' WHERE guild_id='{guild_id}'")
        updated=True
    if double_count is not None:
        cursor.execute(f"UPDATE Counting SET double_count='{double_count}' WHERE guild_id='{guild_id}'")
        updated=True
    if updated:
        connection.commit()
    cursor.close()
    connection.close()






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
def Query(Guild_id,Query):
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
def Configure(Guild_id,Channel_id=None,Double_Count=None,Configure=False):
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