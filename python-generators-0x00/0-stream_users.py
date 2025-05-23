import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def stream_users():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="ALX_prodev"
    )

    cursor = connection.cursor(dictionary=True) # return rows as dicts
    cursor.execute("SELECT * FROM user_data")

    for row in cursor:
        yield row

    cursor.close()
    connection.close()
