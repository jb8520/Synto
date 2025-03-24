import mysql.connector, os

from dotenv import load_dotenv
load_dotenv()


def DataBase_Connection():
    return mysql.connector.connect(host=os.environ['DATABASE_HOST'],user=os.environ['DATABASE_USER'],password=os.environ['DATABASE_PASSWORD'],database=os.environ['DATABASE_NAME'])


def Vc_Creator_Query(guild_id):
    connection=DataBase_Connection()
    cursor=connection.cursor()
    cursor.execute(f"SELECT vc_creator_id FROM Auto_Vc WHERE guild_id='{guild_id}'")
    fetch=cursor.fetchone()
    connection.close()
    if fetch is None:
        Add_Server(guild_id,connection,cursor)
        fetch=[0]
    connection.close()
    cursor.close()
    vc_creator_id=int(fetch[0])
    if vc_creator_id==0:
        return vc_creator_id,'❌ The vc creator channel is not set to a valid channel'
    else:
        return vc_creator_id,'✅ Success!'

def Vc_Category_Query(guild_id):
    connection=DataBase_Connection()
    cursor=connection.cursor()
    cursor.execute(f"SELECT vc_category_id FROM Auto_Vc WHERE guild_id='{guild_id}'")
    fetch=cursor.fetchone()
    connection.close()
    if fetch is None:
        Add_Server(guild_id,connection,cursor)
        fetch=[0]
    connection.close()
    cursor.close()
    vc_category_id=int(fetch[0])
    if vc_category_id==0:
        return vc_category_id,'❌ The vc category is not set to a valid category'
    else:
        return vc_category_id,'✅ Success!'

def Member_Role_Query(guild_id):
    connection=DataBase_Connection()
    cursor=connection.cursor()
    cursor.execute(f"SELECT member_role FROM Auto_Vc WHERE guild_id='{guild_id}'")
    fetch=cursor.fetchone()
    connection.close()
    if fetch is None:
        Add_Server(guild_id,connection,cursor)
        fetch=[0]
    connection.close()
    cursor.close()
    member_role_id=int(fetch[0])
    if member_role_id=='0':
        return member_role_id,'❌ The member role is not set to a valid role'
    else:
        return member_role_id,'✅ Success!'

def Moderator_Roles_Query(guild_id):
    connection=DataBase_Connection()
    cursor=connection.cursor()
    cursor.execute(f"SELECT bypass_roles FROM Auto_Vc WHERE guild_id='{guild_id}'")
    fetch=cursor.fetchone()
    connection.close()
    if fetch is None:
        Add_Server(guild_id,connection,cursor)
        fetch=['0']
    connection.close()
    cursor.close()
    moderator_roles_ids_str=fetch[0]
    moderator_roles_ids_list=[]
    if moderator_roles_ids_str[-1]==',':
        moderator_roles_ids_str=moderator_roles_ids_str[:-1]
    moderator_roles_ids=moderator_roles_ids_str.split(',')
    for id in moderator_roles_ids:
        moderator_roles_ids_list.append(int(id))
    return moderator_roles_ids_list



def Add_Server(guild_id,connection=DataBase_Connection(),cursor=None):
    if cursor is None:
        cursor=connection.cursor()
    cursor.execute(f"INSERT INTO Auto_Vc (guild_id,vc_creator_id,vc_category_id,member_role,bypass_roles) VALUES ('{guild_id}','0','0','0','0')")
    connection.commit()

def Remove_Server(guild_id):
    connection=DataBase_Connection()
    cursor=connection.cursor()
    cursor.execute(f"DELETE FROM Auto_Vc WHERE guild_id='{guild_id}'")
    connection.commit()
    cursor.close()
    connection.close()


def Query(guild_id):
    connection=DataBase_Connection()
    cursor=connection.cursor()
    cursor.execute(f"SELECT * FROM Auto_Vc WHERE guild_id='{guild_id}'")
    fetch=cursor.fetchone()
    if fetch is None:
        Add_Server(guild_id,connection,cursor)
        fetch=(guild_id,0,0,0,'0')
    guild_id,vc_creator_id,vc_category_id,member_role_id,moderator_roles_ids_str=fetch
    vc_creator_id=int(vc_creator_id)
    vc_category_id=int(vc_category_id)
    member_role_id=int(member_role_id)
    moderator_roles_ids_list=[]
    if moderator_roles_ids_str[-1]==',':
        moderator_roles_ids_str=moderator_roles_ids_str[:-1]
    moderator_roles_ids=moderator_roles_ids_str.split(',')
    for id in moderator_roles_ids:
        moderator_roles_ids_list.append(int(id))
    return vc_creator_id,vc_category_id,member_role_id,moderator_roles_ids_list


def Configure(guild_id,vc_creator_id=None,vc_category_id=None,member_role_id=None,moderator_roles_ids_list=None):
    connection=DataBase_Connection()
    cursor=connection.cursor()
    cursor.execute(f"SELECT guild_id FROM Auto_Vc WHERE guild_id='{guild_id}'")
    Fetch=cursor.fetchone()
    if Fetch is None:
        Add_Server(guild_id,connection,cursor)
    updated=False
    if vc_creator_id is not None:
        cursor.execute(f"UPDATE Auto_Vc SET vc_creator_id='{vc_creator_id}' WHERE guild_id='{guild_id}'")
        updated=True
    if vc_category_id is not None:
        cursor.execute(f"UPDATE Auto_Vc SET vc_category_id='{vc_category_id}' WHERE guild_id='{guild_id}'")
        updated=True
    if member_role_id is not None:
        cursor.execute(f"UPDATE Auto_Vc SET member_role='{member_role_id}' WHERE guild_id='{guild_id}'")
        updated=True
    if moderator_roles_ids_list is not None:
        ids_string=''
        for id in moderator_roles_ids_list:
            ids_string+=f'{id},'
        cursor.execute(f"UPDATE Auto_Vc SET bypass_roles='{ids_string}' WHERE guild_id='{guild_id}'")
        updated=True
    if updated:
        connection.commit()
    connection.commit()
    cursor.close()
    connection.close()