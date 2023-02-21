import os
import shutil


def delete_files(path):
    if path.name_image or path.path_to_image or path.path_to_ndvi:
        if path.name_image:
            shutil.rmtree(os.path.abspath(path.name_image))
        if path.path_to_image:
            os.remove(os.path.abspath(path.path_to_image))
        if path.path_to_ndvi:
            os.remove(os.path.abspath(path.path_to_ndvi))
        return True
    return False
