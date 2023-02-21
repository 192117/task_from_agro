import datetime
import json
import os

import geojson
import pandas as pd
from sentinelsat import SentinelAPI, geojson_to_wkt

from config import settings
from zip_worker import extract_image_from_zip


def extract_shots_from_setninelsat(data):
    USER_SENTINEL = settings.USER_SENTINEL
    PASSWORD_SENTINEL = settings.PASSWORD_SENTINEL
    api = SentinelAPI(USER_SENTINEL, PASSWORD_SENTINEL)
    data = geojson.loads(json.dumps(data))
    now_datetime = datetime.datetime.today()
    from_datetime = datetime.datetime(now_datetime.year, month=1, day=1, hour=12, minute=00, second=00)
    footprint = geojson_to_wkt(data)
    products = api.query(footprint,
                         platformname='Sentinel-2',
                         date=(from_datetime, now_datetime),
                         processinglevel='Level-2A',
                         area_relation='Contains',
                         order_by='cloudcoverpercentage',
                         cloudcoverpercentage=(0, 10))
    df = pd.DataFrame(api.to_dataframe(products))
    if df.shape == (0, 0):
        return 0
    else:
        for i in range(df.shape[0]):
            if api.is_online(df.iloc[i]['uuid']):
                filename = df.iloc[i]['title']
                os.mkdir(data.features[0].properties['name'])
                api.download(
                    df.iloc[i]['uuid'],
                    directory_path=os.path.abspath(data.features[0].properties['name'])
                )
                break

        extract_image_from_zip(filename, data['features'][0]['properties']['name'])
        return 1
