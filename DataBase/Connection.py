import mysql.connector, os

from dotenv import load_dotenv
load_dotenv()

def DataBase_Connection():
    return mysql.connector.connect(host=os.environ["DATABASE_HOST"],user=os.environ["DATABASE_USER"],password=os.environ["DATABASE_PASSWORD"],database=os.environ["DATABASE_NAME"])