import mysql.connector, os

from dotenv import load_dotenv
load_dotenv()


def DataBase_Connection():
    return mysql.connector.connect(host=os.environ['DATABASE_HOST'],user=os.environ['DATABASE_USER'],password=os.environ['DATABASE_PASSWORD'],database=os.environ['DATABASE_NAME'])


def Welcome_Channel_Query(guild_id):
    connection=DataBase_Connection()
    cursor=connection.cursor()
    cursor.execute(f"SELECT channel_id FROM Welcome_Message WHERE guild_id='{guild_id}'")
    fetch=cursor.fetchone()
    connection.close()
    if fetch is None:
        Add_Server(guild_id,connection,cursor)
        fetch=[0]
    connection.close()
    cursor.close()
    welcome_channel_id=int(fetch[0])
    if welcome_channel_id==0:
        return welcome_channel_id,'❌ The welcome channel is not set to a valid channel'
    else:
        return welcome_channel_id,'✅ Success!'

def Activated_Query(guild_id):
    connection=DataBase_Connection()
    cursor=connection.cursor()
    cursor.execute(f"SELECT activated FROM Welcome_Message WHERE guild_id='{guild_id}'")
    fetch=cursor.fetchone()
    connection.close()
    if fetch is None:
        Add_Server(guild_id,connection,cursor)
        fetch=['False']
    connection.close()
    cursor.close()
    fetch=fetch[0]
    activated=True if fetch=='True' else False
    return activated,'✅ Success!'



def Add_Server(guild_id,connection=DataBase_Connection(),cursor=None):
    if cursor is None:
        cursor=connection.cursor()
    cursor.execute(f"INSERT INTO Welcome_Message (guild_id, channel_id, title, description, colour, activated) VALUES ('{guild_id}', '0', 'Welcome!','None','None','False')")
    connection.commit()

def Remove_Server(guild_id):
    connection=DataBase_Connection()
    cursor=connection.cursor()
    cursor.execute(f"DELETE FROM Welcome_Message WHERE guild_id='{guild_id}'")
    connection.commit()
    cursor.close()
    connection.close()


def Query(guild_id):
    connection=DataBase_Connection()
    cursor=connection.cursor()
    cursor.execute(f"SELECT * FROM Welcome_Message WHERE guild_id='{guild_id}'")
    fetch=cursor.fetchone()
    if fetch is None:
        Add_Server(guild_id,connection,cursor)
        fetch=(guild_id,0,'Welcome!','None','None',False)
    guild_id,channel_id,title,description,colour,activated=fetch
    guild_id=int(guild_id)
    channel_id=int(channel_id)
    title=str(title)
    description=str(description)
    colour=str(colour)
    activated=True if activated=='True' else False
    return channel_id,title,description,colour,activated


def Configure(guild_id,channel_id=None,title=None,description=None,colour=None,activated=None):
    connection=DataBase_Connection()
    cursor=connection.cursor()
    cursor.execute(f"SELECT guild_id FROM Welcome_Message WHERE guild_id='{guild_id}'")
    Fetch=cursor.fetchone()
    if Fetch is None:
        Add_Server(guild_id,connection,cursor)
    updated=False
    if channel_id is not None:
        channel_id=str(channel_id)
        query="UPDATE Welcome_Message SET channel_id='{}' WHERE guild_id='{}'"
        cursor.execute(query.format(channel_id,guild_id))
        updated=True
    if title is not None:
        title=connection.converter.escape(str(title))
        query="UPDATE Welcome_Message SET title='{}' WHERE guild_id='{}'"
        cursor.execute(query.format(title,guild_id))
        updated=True
    if description is not None:
        description=connection.converter.escape(str(description))
        query="UPDATE Welcome_Message SET description='{}' WHERE guild_id='{}'"
        cursor.execute(query.format(description,guild_id))
        updated=True
    if colour is not None:
        colour=connection.converter.escape(str(colour))
        query="UPDATE Welcome_Message SET colour='{}' WHERE guild_id='{}'"
        cursor.execute(query.format(colour,guild_id))
        updated=True
    if activated is not None:
        activated=str(activated)
        query="UPDATE Welcome_Message SET activated='{}' WHERE guild_id='{}'"
        cursor.execute(query.format(activated,guild_id))
        updated=True
    if updated:
        connection.commit()
    cursor.close()
    connection.close()