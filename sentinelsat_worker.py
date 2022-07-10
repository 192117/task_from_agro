import geojson
import pandas as pd
from sentinelsat import SentinelAPI, geojson_to_wkt
import os, datetime, json, geojson
from zip_worker import worker_zip
from dotenv import load_dotenv

load_dotenv()

def worker_senti(data):
    user_sentinel = os.getenv('user_sentinel')
    password_sentinel = os.getenv('password_sentinel')
    api = SentinelAPI(user_sentinel, password_sentinel)
    data = json.dumps(data)
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

    worker_zip(filename, data['name'])
