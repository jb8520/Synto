import mysql.connector, os

from dotenv import load_dotenv
load_dotenv()

def DataBase_Connection():
    return mysql.connector.connect(host=os.environ["DATABASE_HOST"],user=os.environ["DATABASE_USER"],password=os.environ["DATABASE_PASSWORD"],database=os.environ["DATABASE_NAME"])

def Query(Guild_id,Query):
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute(f"SELECT {Query} FROM Welcome_Message WHERE guild_id='{Guild_id}'")
    Fetch=(Cursor.fetchone())[0]
    if Query=="activated":
        Fetch= True if Fetch=="True" else False
    elif Query=="guild_id" or Query=="channel_id":
        Fetch=int(Fetch)
    Connection.commit()
    Connection.close()
    return Fetch

def Configure(Guild_id,Channel_id=None,Title=None,Description=None,Colour=None,Activated=None):
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute(f"SELECT guild_id FROM Welcome_Message WHERE guild_id='{Guild_id}'")
    Fetch=Cursor.fetchone()
    if Fetch is None:
        Cursor.execute(f"INSERT INTO Welcome_Message(guild_id, channel_id, title, description, colour, activated) VALUES ('{Guild_id}', '0', 'Welcome!','None','None','False')")
        Connection.commit()
    if Channel_id is not None:
        Cursor.execute(f"UPDATE Welcome_Message SET channel_id='{Channel_id}' WHERE guild_id='{Guild_id}'")
    if Title is not None:
        Cursor.execute(f"UPDATE Welcome_Message SET title='{Title}' WHERE guild_id='{Guild_id}'")
    if Description is not None:
        Cursor.execute(f"UPDATE Welcome_Message SET description='{Description}' WHERE guild_id='{Guild_id}'")
    if Colour is not None:
        Cursor.execute(f"UPDATE Welcome_Message SET colour='{Colour}' WHERE guild_id='{Guild_id}'")
    if Activated is not None:
        Cursor.execute(f"UPDATE Welcome_Message SET activated='{Activated}' WHERE guild_id='{Guild_id}'")
    Connection.commit()
    Cursor.close()
    Connection.close()
def Remove(Guild_id):
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute(f"DELETE FROM Welcome_Message WHERE guild_id='{Guild_id}'")
    Connection.commit()
    Cursor.close()
    Connection.close()