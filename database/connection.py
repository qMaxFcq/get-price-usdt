from os import getcwd, getenv
from sys import path
from dotenv import load_dotenv
from urllib.parse import urlparse
from mysql.connector import connect, Error, MySQLConnection

# -------- Append Root Folder to Path --------
path.append(getcwd())
try:
    load_dotenv(".env")
except ImportError:
    pass

def connect_db() -> MySQLConnection:
    DB_URL = getenv("DB_URL")
    url = urlparse(DB_URL)
    db_config = {
        "host": url.hostname,
        "port": url.port,
        "user": url.username,
        "password": url.password,
        "database": url.path[1:],
    }
    try:
        connection = connect(**db_config)
        # print('con done')
        return connection
    except Error as err:
        print("Error connecting to MySQL database:", err)


def close_connect_db(connection: MySQLConnection):
    if connection is not None:
        connection.close()

