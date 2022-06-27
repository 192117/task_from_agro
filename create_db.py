import psycopg2

def start_db():
    con = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="postgres",
        host="127.0.0.1",
        port="5432"
    )

    cur = con.cursor()
    cur.execute('''CREATE TABLE FIELDS  
         (ID SERIAL PRIMARY KEY,
         NAME CHAR(100) UNIQUE NOT NULL,
         IMAGE TEXT UNIQUE NOT NULL,
         NDVI TEXT UNIQUE NOT NULL);''')

    con.commit()
    con.close()