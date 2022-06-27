from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from sentinelsat_worker import worker_senti
from make_image import images_make
import os, shutil, psycopg2
from create_db import start_db

app = FastAPI()
# start_db()

con = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="postgres",
        host="127.0.0.1",
        port="5432"
    )

@app.post('/add')
async def post_field(request: Request):
    data = await request.json()
    try:
        worker_senti(data)
        cur = con.cursor()
        cur.execute("SELECT * FROM fields WHERE name = %s", (data['name'],))
        if len(cur.fetchall()) == 0:
            cur.execute("INSERT INTO fields (name, image, ndvi) VALUES (%s, %s, %s)", (data['name'], '', ''))
            con.commit()
        else:
            raise HTTPException(status_code=208, detail="This field name already exists.")
    except AttributeError:
        raise HTTPException(status_code=400, detail="It's not GEOJSON")

    return f'Success! For NDVI and SNAPSHOT, use the name = {data["name"]}.'


@app.get('/delete/')
async def delete_field(name: str):
    cur = con.cursor()
    cur.execute("SELECT name, image, ndvi FROM fields WHERE name = %s", (name,))
    rows = cur.fetchall()
    if len(cur.fetchall()) != 0:
        cur.execute("DELETE * FROM fields WHERE name = %s", (name,))
        con.commit()
        shutil.rmtree(os.path.abspath(rows[0][0]))
        shutil.rmtree(os.path.abspath(rows[0][1]))
        shutil.rmtree(os.path.abspath(rows[0][2]))
    else:
        raise HTTPException(status_code=204, detail="There is no such field.")


@app.get('/ndvi/')
async def ndvi_field(name: str):
    if name:
        cur = con.cursor()
        cur.execute("UPDATE fields set ndvi = %s where name = %s", (images_make('ndvi', name), name))
        con.commit()
        cur.execute("SELECT ndvi FROM fields WHERE name = %s", (name,))
        path = cur.fetchone()
        return FileResponse(path[0])
    else:
        return 'It is necessary to send arguments'

@app.get('/show/')
async def show_field(name: str):
    if name:
        cur = con.cursor()
        cur.execute(f"UPDATE fields set image = %s WHERE name = %s", (images_make('show', name), name))
        con.commit()
        cur.execute(f"SELECT image FROM fields WHERE name = %s", (name,))
        path = cur.fetchone()
        return FileResponse(path[0])
    else:
        return 'It is necessary to send arguments'

