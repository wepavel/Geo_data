from sentinelsat.sentinel import SentinelAPI
import geopandas as gpd
from flask import Response
import os
from osgeo import gdal
import configparser
import numpy as np


def read_ini(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    conf_dict = {}
    for section in config.sections():
        for key in config[section]:
            conf_dict[key] = config[section][key]
            print((key, config[section][key]))
    return conf_dict


class PictureModel:
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


class PictureFabric:
    """."""

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

    def get_pictures(self, **kwargs: object) -> list[PictureModel]:

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
        pictures = []

        for picture in products:

            ident = products[picture]['identifier']
            granule = products[picture]['granuleidentifier']
            datastrip = products[picture]['datastripidentifier']

            parts1 = ident.split('_')
            parts2 = datastrip.split('_')
            parts2[7] = parts2[7].replace(parts2[7][0], '')
            parts3 = granule.split('_')

            uuid = picture
            some_ident = f'{parts2[3]}_{parts1[5]}_{parts3[7]}_{parts2[7]}'
            img_ident = f'{parts1[5]}_{parts1[2]}'

            resp_path = eval(f'f"""{self.path}"""')
            resp_path = resp_path + 'Nodes'

            img_resp = self.api.session.get(resp_path)

            if img_resp.status_code == 200:
                preview = f'http://localhost:1060//preview/{picture}'
                download = f"http://localhost:1060//download/{picture}/{ident}/{parts2[3]}_\
{parts1[5]}_{parts3[7]}_{parts2[7]}/{parts1[5]}_{parts1[2]}"

                pictures.append(
                    PictureModel(date=products[picture]['generationdate'], name=products[picture]['title'],
                                 uuid=picture, prev=preview, download=download)
                )
        return pictures

    def get_preview(self, uuid):

        path = eval(f'f"""{self.prev_path}"""')
        resp = self.api.session.get(path)

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response

    def get_picture(self, uuid, ident, some_ident, img_ident):

        path = eval(f'f"""{self.path}"""')
        path = path + '$value'

        resp = self.api.session.get(path)
        if resp.status_code == 200:

            photo = resp.content

            gdal.FileFromMemBuffer(f'/vsimem/{uuid}.jp2', photo)
            ds = gdal.Open(f'/vsimem/{uuid}.jp2', gdal.GA_Update)

            ds1 = gdal.Translate(f'/vsimem/{uuid}.tif', f'/vsimem/{uuid}.jp2')
            gdal.Unlink(f'/vsimem/{uuid}.jp2')
            ds = None

            warp = gdal.Warp(f'/vsimem/{uuid}.tif', ds1, dstAlpha=True, dstSRS='EPSG:3857',
                             outputType=gdal.gdalconst.GDT_Byte)
            ds1 = None

            f = gdal.VSIFOpenL(f'/vsimem/{uuid}.tif', 'rb')

            gdal.VSIFSeekL(f, 0, 2)  # поиск конца
            size = gdal.VSIFTellL(f)
            gdal.VSIFSeekL(f, 0, 0)  # поиск начала
            data = bytes(gdal.VSIFReadL(1, size, f))
            gdal.VSIFCloseL(f)

            warp = None
            f = None

            gdal.Unlink(f'/vsimem/{uuid}.tif')

            resp = Response(data, mimetype='image/tif')

            resp.headers['Content-Disposition'] = f'attachment; filename={uuid}.tif'
            return resp
        else:
            return 'Error with downloading picture'
