import json, geojson, os
from fastapi import FastAPI, Request, HTTPException
from sentinelsat_worker import worker_senti
from zip_worker import worker_zip
from make_image import images_make
# from create_db import *
# from sqlalchemy.orm import sessionmaker
#
# Session = sessionmaker(bind = db)
# session = Session()


app = FastAPI()


@app.post('/add')
async def post_field(request: Request):
    data = await request.json()
    try:
        filename, name = worker_senti(data)
        worker_zip(filename, name)
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
    data = json.dumps(data)
    try:
        data = geojson.loads(data)
        data.is_valid
        if len(session.query(Fields).filter(Fields.name == data['name']).all()) != 0:
            session.query(Fields).filter(Fields.name == data['name']).delete()
            session.commit()
        else:
            raise HTTPException(status_code=204, detail="There is no such field.")
    except AttributeError:
        raise HTTPException(status_code=400, detail="It's not GEOJSON")

    return f'Success!'

@app.post('/ndvi')
async def ndvi_field(request: Request):
    data = await request.json()
    return images_make('ndvi', data['name'])


@app.post('/show')
async def show_field(request: Request):
    data = await request.json()
    return images_make('show', data['name'])

