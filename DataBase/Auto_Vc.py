import mysql.connector, os

from dotenv import load_dotenv
load_dotenv()

def DataBase_Connection():
    return mysql.connector.connect(host=os.environ["DATABASE_HOST"],user=os.environ["DATABASE_USER"],password=os.environ["DATABASE_PASSWORD"],database=os.environ["DATABASE_NAME"])

def Query(Guild_id,Query):
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute(f"SELECT {Query} FROM Auto_Vc WHERE guild_id='{Guild_id}'")
    Fetch=Cursor.fetchone()
    Connection.commit()
    Connection.close()
    if Fetch is None:
        Configure(Guild_id,Configure=True)
        Cursor.execute(f"SELECT {Query} FROM Auto_Vc WHERE guild_id='{Guild_id}'")
        Fetch=Cursor.fetchone()
    Cursor.close()
    if Fetch[0]=="0":
        return 0
    if Query=="bypass_roles":
        List=Fetch[0][:-1].split(",")
        ids=[]
        for id in List:
            ids.append(int(id))
        return ids
    return int(Fetch[0])
def Configure(Guild_id,Vc_Creator_id=None,Vc_Category_id=None,Member_Role=None,Bypass_Roles=None,Configure=False):
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    if Configure:
        Cursor.execute(f"INSERT INTO Auto_Vc (guild_id,vc_creator_id,vc_category_id,member_role,bypass_roles) VALUES ('{Guild_id}','0','0','0','0')")
        Connection.commit()
    else:
        Cursor.execute(f"SELECT guild_id FROM Auto_Vc WHERE guild_id='{Guild_id}'")
        Fetch=Cursor.fetchone()
        if Fetch is None:
            Cursor.execute(f"INSERT INTO Auto_Vc (guild_id,vc_creator_id,vc_category_id,member_role,bypass_roles) VALUES ('{Guild_id}','0','0','0','0')")
            Connection.commit()
    if Vc_Creator_id is not None:
        Cursor.execute(f"UPDATE Auto_Vc SET vc_creator_id='{Vc_Creator_id}' WHERE guild_id='{Guild_id}'")
    if Vc_Category_id is not None:
        Cursor.execute(f"UPDATE Auto_Vc SET vc_category_id='{Vc_Category_id}' WHERE guild_id='{Guild_id}'")
    if Member_Role is not None:
        Cursor.execute(f"UPDATE Auto_Vc SET member_role='{Member_Role}' WHERE guild_id='{Guild_id}'")
    if Bypass_Roles is not None:
        ids=""
        for id in Bypass_Roles:
            ids+=f"{id},"
        Cursor.execute(f"UPDATE Auto_Vc SET bypass_roles='{ids}' WHERE guild_id='{Guild_id}'")
    Connection.commit()
    Cursor.close()
    Connection.close()
def Remove(Guild_id):
    Connection=DataBase_Connection()
    Cursor=Connection.cursor()
    Cursor.execute(f"DELETE FROM Auto_Vc WHERE guild_id='{Guild_id}'")
    Connection.commit()
    Cursor.close()
    Connection.close()