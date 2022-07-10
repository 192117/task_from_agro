import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

def start_db():
    name_db = os.getenv('name_db')
    user_db = os.getenv('user_db')
    password_db = os.getenv('password_db')
    host_db = os.getenv('host_db')
    port_db = os.getenv('port_db')
    con = psycopg2.connect(
        database=name_db,
        user=user_db,
        password=password_db,
        host=host_db,
        port=port_db
    )

    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS FIELDS  
         (ID SERIAL PRIMARY KEY,
         NAME CHAR(100) UNIQUE NOT NULL,
         IMAGE TEXT UNIQUE,
         NDVI TEXT UNIQUE);''')

    con.commit()
    con.close()

start_db()
