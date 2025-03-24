import mysql.connector, os

from dotenv import load_dotenv
load_dotenv()


def DataBase_Connection():
    return mysql.connector.connect(host=os.environ['DATABASE_HOST'],user=os.environ['DATABASE_USER'],password=os.environ['DATABASE_PASSWORD'],database=os.environ['DATABASE_NAME'])


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
    cursor.execute(f"SELECT double_count FROM Counting WHERE guild_id='{guild_id}'")
    fetch=cursor.fetchone()
    connection.close()
    if fetch is None:
        Add_Server(guild_id,connection,cursor)
        fetch=['False']
    connection.close()
    cursor.close()
    fetch=fetch[0]
    double_count=True if fetch=='True' else False
    return double_count,'✅ Success!'



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
    guild_id=int(guild_id)
    channel_id=int(channel_id)
    highscore=int(highscore)
    current_score=int(current_score)
    message_id=int(message_id)
    author_id=int(author_id)
    double_count=True if double_count=='True' else False
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
        channel_id=str(channel_id)
        query="UPDATE Counting SET channel_id='{}' WHERE guild_id='{}'"
        cursor.execute(query.format(channel_id,guild_id))
        updated=True
    if double_count is not None:
        double_count=str(double_count)
        query="UPDATE Counting SET double_count='{}' WHERE guild_id='{}'"
        cursor.execute(query.format(double_count,guild_id))
        updated=True
    if updated:
        connection.commit()
    cursor.close()
    connection.close()