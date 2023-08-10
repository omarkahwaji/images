import os
import time
import mysql.connector
from mysql.connector import Error

def connect():
    """ Try to establish a connection to MySQL """
    try:
        conn = mysql.connector.connect(host=os.getenv("DB_HOST"),
                                       database=os.getenv("DB_NAME"),
                                       user=os.getenv("DB_USER"),
                                       password=os.getenv("DB_PASS"))
        if conn.is_connected():
            print('Connected to MySQL database')
            conn.close()
            return True
    except Error as e:
        print(e)
        return False

while not connect():
    print("Unable to connect to the database. Retrying...")
    time.sleep(1)

print("Database is up!")
