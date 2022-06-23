import json, geojson, datetime, os, zipfile
from fastapi import FastAPI, Request, HTTPException
import pandas as pd
from sentinelsat import SentinelAPI, geojson_to_wkt
import rasterio as rio
# from create_db import *
# from sqlalchemy.orm import sessionmaker
#
# Session = sessionmaker(bind = db)
# session = Session()


app = FastAPI()
api = SentinelAPI('lakaka', '123456lakaka!')


@app.post('/add')
async def post_field(request: Request):
    data = await request.json()
    data = json.dumps(data)
    try:
        data = geojson.loads(data)
        data.is_valid
        n = datetime.datetime.today()
        s = datetime.datetime(n.year, month=1, day=1, hour=12, minute=00, second=00)
        footprint = geojson_to_wkt(data)
        products = api.query(footprint,
                             platformname='Sentinel-2',
                             date=(s, n),
                             processinglevel='Level-2A',
                             area_relation='Contains',
                             order_by='cloudcoverpercentage',
                             cloudcoverpercentage=(0, 10))
        df = pd.DataFrame(api.to_dataframe(products))
        for i in range(df.shape[0]):
            if api.is_online(df.iloc[i]['uuid']):
                filename = df.iloc[i]['title']
                os.mkdir(data['name'])
                api.download(df.iloc[i]['uuid'], directory_path=os.path.abspath(data['name']))
                break
        names = ['_B02_10m', '_B03_10m', '_B04_10m', '_B08_10m']
        z = zipfile.ZipFile(os.path.join(os.path.abspath(data['name']), filename + '.zip'))
        for zip_info in z.infolist():
            name, extension = os.path.splitext(zip_info.filename)
            if extension == '.jp2':
                if names[0] in name or names[1] in name or names[2] in name or names[3] in name:
                    zip_info.filename = os.path.basename(zip_info.filename)
                    z.extract(zip_info, os.path.abspath(data['name']))
        z.close()
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
    path = os.path.abspath(data['name'])
    tree = list(os.walk(path))
    for i in tree[0][-1]:
        name, extension = os.path.splitext(i)
        if extension == '.jp2':
            if '_B04' in name:
                b4 = rio.open(os.path.join(path, i))
            elif '_B08' in name:
                b8 = rio.open(os.path.join(path, i))

    # read Red(b4) and NIR(b8) as arrays
    red = b4.read()
    nir = b8.read()

    # Calculate ndvi
    ndvi = (nir.astype(float) - red.astype(float)) / (nir + red)

    # Write the NDVI image
    meta = b4.meta
    meta.update(driver='GTiff')
    meta.update(dtype=rio.float32)

    with rio.open(f'{data["name"]}_ndvi.tif', 'w', **meta) as dst:
        dst.write(ndvi.astype(rio.float32))

    return f'Success! Links for download:'

@app.post('/show')
async def show_field(request: Request):
    data = await request.json()
    path = os.path.abspath(data['name'])
    tree = list(os.walk(path))
    for i in tree[0][-1]:
        name, extension = os.path.splitext(i)
        if extension == '.jp2':
            if '_B04' in name:
                b4 = rio.open(os.path.join(path, i))
            elif '_B03' in name:
                b3 = rio.open(os.path.join(path, i))
            elif '_B02' in name:
                b2 = rio.open(os.path.join(path, i))

    # Create an RGB image
    with rio.open(f'{data["name"]}.tiff', 'w', driver='Gtiff', width=b4.width, height=b4.height,
                  count=3, crs=b4.crs, transform=b4.transform, dtype=b4.dtypes[0]) as rgb:
        rgb.write(b2.read(1), 1)
        rgb.write(b3.read(1), 2)
        rgb.write(b4.read(1), 3)
        rgb.close()

    return f'Success! Links for download:'
