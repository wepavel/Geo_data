# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
import os
import configparser
from sentinelsat.sentinel import SentinelAPI
import geopandas as gpd
from flask import Response
from osgeo import gdal


def read_ini(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    conf_dict = {}
    for section in config.sections():
        for key in config[section]:
            conf_dict[key] = config[section][key]
            print((key, config[section][key]))
    return conf_dict


class ImageModel:
    """."""

    def __init__(self, date: str, name: str, uuid: str, prev: str, download: str):
        """."""
        self._date = date
        self._name = name
        self._uuid = uuid
        self._prev = prev
        self._download = download

    def to_dict(self) -> dict:
        return {
            'date': self._date,
            'name': self._name,
            'uuid': self._uuid,
            'preview_url': self._prev,
            'download_url': self._download
        }


class ImageFabric:
    """Tools for"""

    def __init__(self):
        """."""

        self.cur_dir = os.getcwd()
        path = self.cur_dir + '/conf.ini'
        print(path)
        config = read_ini(self.cur_dir + '/conf.ini')
        print(config)
        user = config['username']
        password = config['password']
        self.path = config['download_path']
        self.prev_path = config['preview_path']
        self.api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')

    def get_images(self, **kwargs: object) -> list[ImageModel]:
        """Check available images on request"""

        boundary = gpd.GeoDataFrame.from_features(kwargs["features"])
        footprint = None
        for i in boundary['geometry']:
            footprint = i

        date = kwargs['features'][0]['properties']['date']
        clouds = kwargs['features'][0]['properties']['cloud']
        products = self.api.query(footprint,
                                  date=(date[0], date[1]),
                                  platformname='Sentinel-2',
                                  processinglevel='Level-2A',
                                  cloudcoverpercentage=(clouds[0], clouds[1]))
        images = []

        for image in products:
            # Creating an image url path

            ident = products[image]['identifier']
            granule = products[image]['granuleidentifier']
            datastrip = products[image]['datastripidentifier']

            parts1 = ident.split('_')
            parts2 = datastrip.split('_')
            parts2[7] = parts2[7].replace(parts2[7][0], '')
            parts3 = granule.split('_')

            uuid = image
            path_1 = f'{parts2[3]}_{parts1[5]}_{parts3[7]}_{parts2[7]}'
            path_2 = f'{parts1[5]}_{parts1[2]}'

            resp_path = eval(f'f"""{self.path}"""')
            resp_path = resp_path + 'Nodes'

            img_resp = self.api.session.get(resp_path)

            if img_resp.status_code == 200:
                # Check if image is available
                preview = f'http://localhost:1060//preview/{uuid}'
                download = f"http://localhost:1060//download/{uuid}/{ident}/{path_1}/{path_2}"

                images.append(
                    ImageModel(date=products[image]['generationdate'],
                               name=products[image]['title'],
                               uuid=image, prev=preview, download=download)
                )
        return images

    def get_preview(self, uuid):
        """Get preview image by uuid"""

        path = eval(f'f"""{self.prev_path}"""')
        resp = self.api.session.get(path)

        excluded_headers = ['content-encoding', 'content-length',
                            'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response

    def get_image(self, uuid, ident, path_1, path_2):
        """Get image in .tof format in EPSG:3857 projection"""

        path = eval(f'f"""{self.path}"""')
        path = path + '$value'

        resp = self.api.session.get(path)
        if resp.status_code == 200:
            pass
        else:
            return 'Error with downloading image'

        photo = resp.content

        gdal.FileFromMemBuffer(f'/vsimem/{uuid}.jp2', photo)
        img_gp2 = gdal.Open(f'/vsimem/{uuid}.jp2', gdal.GA_Update)

        img_tif = gdal.Translate(f'/vsimem/{uuid}.tif', f'/vsimem/{uuid}.jp2')
        gdal.Unlink(f'/vsimem/{uuid}.jp2')
        img_gp2 = None

        img_epsg_3857 = gdal.Warp(f'/vsimem/{uuid}.tif', img_tif,
                                  dstAlpha=True, dstSRS='EPSG:3857',
                                  outputType=gdal.gdalconst.GDT_Byte
                                  )
        img_tif = None

        img_obj = gdal.VSIFOpenL(f'/vsimem/{uuid}.tif', 'rb')

        gdal.VSIFSeekL(img_obj, 0, 2)  # поиск конца
        size = gdal.VSIFTellL(img_obj)
        gdal.VSIFSeekL(img_obj, 0, 0)  # поиск начала
        data = bytes(gdal.VSIFReadL(1, size, img_obj))
        gdal.VSIFCloseL(img_obj)

        img_epsg_3857 = None
        img_obj = None

        gdal.Unlink(f'/vsimem/{uuid}.tif')

        resp = Response(data, mimetype='image/tif')

        resp.headers['Content-Disposition'] = f'attachment; filename={uuid}.tif'
        return resp
