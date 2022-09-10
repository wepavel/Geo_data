from sentinelsat.sentinel import SentinelAPI
import geopandas as gpd
from flask import Response, send_from_directory, send_file
import os
from osgeo import gdal


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
        user = 'wepaul'
        password = 'Sporopedu123'
        self.api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')
        self.cur_dir = os.getcwd()

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

            resp_path = f"https://scihub.copernicus.eu/dhus/odata/v1/Products('{picture}')/Nodes('{ident}.SAFE')/Nodes('GRANULE')\
/Nodes('{parts2[3]}_{parts1[5]}_{parts3[7]}_{parts2[7]}')/Nodes('IMG_DATA')/Nodes('R10m')/Nodes('{parts1[5]}_{parts1[2]}_TCI_10m.jp2')/Nodes"

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

        path = f"https://scihub.copernicus.eu/dhus/odata/v1/Products('{uuid}')/Products('Quicklook')/$value"

        resp = self.api.session.get(path)

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response

    def get_picture(self, uuid, ident, some_ident, img_ident):

        path = f"https://scihub.copernicus.eu/dhus/odata/v1/Products('{uuid}')/Nodes('{ident}.SAFE')/Nodes('GRANULE')\
/Nodes('{some_ident}')/Nodes('IMG_DATA')/Nodes('R10m')/Nodes('{img_ident}_TCI_10m.jp2')/$value"

        resp = self.api.session.get(path)
        if resp.status_code == 200:

            photo = resp.content

            gdal.FileFromMemBuffer('/vsimem/inmem.jp2', photo)
            ds = gdal.Open('/vsimem/inmem.jp2')

            warp = gdal.Warp('/vsimem/inmem_3857.jp2', ds, dstSRS='EPSG:3857', outputType=gdal.gdalconst.GDT_Byte)

            ds1 = gdal.Translate(f'/vsimem/{uuid}.tif', '/vsimem/inmem_3857.jp2')

            f = gdal.VSIFOpenL(f'/vsimem/{uuid}.tif', 'rb')
            gdal.VSIFSeekL(f, 0, 2)  # поиск конца
            size = gdal.VSIFTellL(f)
            gdal.VSIFSeekL(f, 0, 0)  # поиск начала
            data = bytes(gdal.VSIFReadL(1, size, f))
            gdal.VSIFCloseL(f)

            ds1 = None
            warp = None
            ds = None

            gdal.Unlink('/vsimem/inmem.jp2')
            gdal.Unlink('/vsimem/inmem_3857.jp2')
            gdal.Unlink(f'/vsimem/{uuid}.tif')

            resp = Response(data, mimetype='image/tif')

            resp.headers['Content-Disposition'] = f'attachment; filename={uuid}.tif'
            return resp
        else:
            return 'Error with downloading picture'
