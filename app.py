from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from sentinelsat_worker import worker_senti
from make_image import images_make
import os, shutil
from create_db import *
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind = db)
session = Session()


app = FastAPI()


@app.post('/add')
async def post_field(request: Request):
    data = await request.json()
    try:
        worker_senti(data)
        if len(session.query(Fields).filter(Fields.name == data['name']).all()) == 0:
            field = Fields(name=data['name'], data=geojson.dumps(data))
            session.add(field)
            session.commit()
        else:
            raise HTTPException(status_code=208, detail="This field name already exists.")
    except AttributeError:
        raise HTTPException(status_code=400, detail="It's not GEOJSON")

    return f'Success! For NDVI and SNAPSHOT, use the name = {data["name"]}.'


@app.delete('/delete')
async def delete_field(request: Request):
    data = await request.json()
    if len(session.query(Fields).filter(Fields.name == data['name']).all()) != 0:
        session.query(Fields).filter(Fields.name == data['name']).delete()
        session.commit()
        shutil.rmtree(os.path.abspath(data['name'])
    else:
        raise HTTPException(status_code=204, detail="There is no such field.")

    return f'Success!'

@app.post('/ndvi')
async def ndvi_field(request: Request):
    data = await request.json()
    return FileResponse(images_make('ndvi', data['name']))


@app.post('/show')
async def show_field(request: Request):
    data = await request.json()
    return FileResponse(images_make('show', data['name']))

