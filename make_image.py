import os
import rasterio as rio


def images_make(type, full_name):
    path = os.path.abspath(full_name)
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
            elif '_B08' in name:
                b8 = rio.open(os.path.join(path, i))

    if type == 'ndvi':

        red = b4.read()
        nir = b8.read()

        ndvi = (nir.astype(float) - red.astype(float)) / (nir + red)

        meta = b4.meta
        meta.update(driver='GTiff')
        meta.update(dtype=rio.float32)

        with rio.open(f'{full_name}_ndvi.tif', 'w', **meta) as dst:
            dst.write(ndvi.astype(rio.float32))

        links = os.path.abspath(f'{full_name}_ndvi.tif')

    elif type == 'show':

        with rio.open(f'{full_name}.tiff', 'w', driver='Gtiff', width=b4.width, height=b4.height,
                      count=3, crs=b4.crs, transform=b4.transform, dtype=b4.dtypes[0]) as rgb:
            rgb.write(b2.read(1), 1)
            rgb.write(b3.read(1), 2)
            rgb.write(b4.read(1), 3)
            rgb.close()

        links = os.path.abspath(f'{full_name}.tiff')

    return links