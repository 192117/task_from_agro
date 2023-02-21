import json

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from create_db import connect_db, start_db
from make_image import make_image_for_user
from models import GeoJSONFeatureCollection
from sentinelsat_worker import extract_shots_from_setninelsat
from utils import delete_files

app = FastAPI()


@app.on_event('startup')
async def startup_event():
    start_db()


@app.on_event('shutdown')
async def shutdown_event():
    connect_db().close()


@app.post('/add/', response_class=JSONResponse)
async def add_object(request: Request, db: Session = Depends(connect_db)):
    try:
        from create_db import Image
        data = await request.json()
        geojson_data = GeoJSONFeatureCollection(**data)
        result = db.query(Image.name_image).filter(
            Image.name_image == geojson_data.features[0].properties['name']
        ).first()
        if result is None:
            if extract_shots_from_setninelsat(data) == 1:
                new_image = Image(name_image=geojson_data.features[0].properties['name'])
                db.add(new_image)
                db.commit()
                db.refresh(new_image)
                return JSONResponse(
                    {'detail': f'Success! For NDVI and SNAPSHOT, use the name = {new_image.name_image}.'},
                    status_code=200
                )
            else:
                raise HTTPException(status_code=404, detail="The satellite has no images.")
        else:
            raise HTTPException(status_code=208, detail="This parameter name already exists.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except json.JSONDecodeError:
        raise HTTPException(status_code=415, detail="It's not JSON")


@app.get('/delete/', response_class=JSONResponse)
async def delete_object(name: str, db: Session = Depends(connect_db)):
    from create_db import Image
    result = db.query(Image).filter(Image.name_image == name).first()
    if result:
        if delete_files(result):
            db.query(Image).filter(Image.name_image == name).delete()
            db.commit()
            return JSONResponse({'detail': 'Success!'}, status_code=200)
        else:
            return JSONResponse({'detail': 'Something wrong on server!'}, status_code=500)
    else:
        return JSONResponse({'detail': 'This parameter name does not exist.'}, status_code=404)


@app.get('/ndvi/', response_class=FileResponse)
async def get_ndvi_image(name: str, db: Session = Depends(connect_db)):
    if name:
        try:
            from create_db import Image
            result = db.query(Image.path_to_ndvi).filter(Image.name_image == name).first()
            if result[0]:
                path_to_ndvi = result[0]
            else:
                path_to_ndvi = make_image_for_user('ndvi', name)
                db.query(Image).filter(Image.name_image == name).update({'path_to_ndvi': path_to_ndvi})
                db.commit()
            return FileResponse(path=path_to_ndvi, filename=path_to_ndvi.split('/')[-1])
        except IndexError:
            return JSONResponse({'detail': 'Incorrect name'}, status_code=404)
    else:
        return JSONResponse({'detail': 'It is necessary to send arguments'}, status_code=400)


@app.get('/show/', response_class=FileResponse)
async def get_image(name: str, db: Session = Depends(connect_db)):
    if name:
        try:
            from create_db import Image
            result = db.query(Image.path_to_image).filter(Image.name_image == name).first()
            if result[0]:
                path_to_image = result[0]
            else:
                path_to_image = make_image_for_user('show', name)
                db.query(Image).filter(Image.name_image == name).update({'path_to_image': path_to_image})
                db.commit()
            return FileResponse(path=path_to_image, filename=path_to_image.split('/')[-1])
        except IndexError:
            return JSONResponse({'detail': 'Incorrect name'}, status_code=404)
    else:
        return JSONResponse({'detail': 'It is necessary to send arguments'}, status_code=400)
