import os, zipfile


def worker_zip(filename, name):
    names = ['_B02_10m', '_B03_10m', '_B04_10m', '_B08_10m']
    z = zipfile.ZipFile(os.path.join(os.path.abspath(name), filename + '.zip'))
    for zip_info in z.infolist():
        name_full, extension = os.path.splitext(zip_info.filename)
        if extension == '.jp2':
            if names[0] in name_full or names[1] in name_full or names[2] in name_full or names[3] in name_full:
                zip_info.filename = os.path.basename(zip_info.filename)
                z.extract(zip_info, os.path.abspath(name))
    z.close()

def image_zip(filepath, full_name, type):
    if type == 'ndvi':
        with zipfile.ZipFile(f'{full_name}ndvi.zip', 'w') as myzip:
            myzip.write(filepath)
        return f'{full_name}ndvi.zip'
    elif type == 'show':
        with zipfile.ZipFile(f'{full_name}.zip', 'w') as myzip:
            myzip.write(filepath)
        return f'{full_name}.zip'
