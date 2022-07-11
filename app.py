from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from sentinelsat_worker import worker_senti
from make_image import images_make
import os, shutil
import psycopg2
import create_db
from dotenv import load_dotenv

load_dotenv()

name_db = os.getenv('name_db')
user_db = os.getenv('user_db')
password_db = os.getenv('password_db')
host_db = os.getenv('host_db')
port_db = os.getenv('port_db')

app = FastAPI()

con = psycopg2.connect(
        database=name_db,
        user=user_db,
        password=password_db,
        host=host_db,
        port=port_db
    )


@app.post('/add')
async def post_field(request: Request):
    try:
        data = await request.json()
        cur = con.cursor()
        cur.execute("SELECT * FROM fields WHERE name = %s", (data['name'],))
        if cur.fetchone() is None:
            if worker_senti(data) == 1:
                cur.execute("INSERT INTO fields (name) VALUES (%s)", (data['name'],))
                con.commit()
            else:
                raise HTTPException(status_code=200, detail="The satellite has no images.")
        else:
            raise HTTPException(status_code=208, detail="This parameter name already exists.")
    except AttributeError:
        raise HTTPException(status_code=400, detail="It's not GEOJSON")
    except KeyError:
        raise HTTPException(status_code=400, detail="I can't find the parameter name")

    return f'Success! For NDVI and SNAPSHOT, use the name = {data["name"]}.'


@app.get('/delete/')
async def delete_field(name: str):
    cur = con.cursor()
    cur.execute("SELECT * FROM fields WHERE name = %s", (name,))
    rows = cur.fetchall()
    if len(rows) != 0:
        shutil.rmtree(os.path.abspath(rows[0][1]).replace(' ', ''))
        os.remove(os.path.abspath(rows[0][2]).replace(' ', ''))
        os.remove(os.path.abspath(rows[0][3]).replace(' ', ''))
        cur.execute("DELETE FROM fields WHERE name = %s", (name,))
        con.commit()
        return 'Success!'
    else:
        return 'This parameter name does not exist.'


@app.get('/ndvi/')
async def ndvi_field(name: str):
    if name:
        try:
            image = images_make('ndvi', name)
            cur = con.cursor()
            cur.execute("UPDATE fields set ndvi = %s WHERE name = %s", (image, name))
            con.commit()
            cur.close()
            return FileResponse(image)
        except IndexError:
            return 'Incorrect name'
    else:
        return 'It is necessary to send arguments'


@app.get('/show/')
async def show_field(name: str):
    if name:
        try:
            image = images_make('show', name)
            cur = con.cursor()
            cur.execute(f"UPDATE fields set image = %s WHERE name = %s", (image, name))
            con.commit()
            cur.close()
            return FileResponse(image)
        except IndexError:
            return 'Incorrect name'
    else:
        return 'It is necessary to send arguments'