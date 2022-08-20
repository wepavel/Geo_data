from sentinelsat.sentinel import SentinelAPI
import geopandas as gpd
from flask import Flask, request, redirect, Response
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

    def get_pictures(self, **kwargs: object) -> list[PictureModel]:

        # boundary = gpd.read_file(Json_dir)

        boundary = gpd.GeoDataFrame.from_features(kwargs["features"])
        footprint = None
        for i in boundary['geometry']:
            footprint = i

        # print(kwargs['features'][0]['properties']['date'])
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

            preview = f'http://localhost:1060//preview/{picture}'
            download = f"http://localhost:1060//download/{picture}/{ident}/{parts2[3]}_\
{parts1[5]}_{parts3[7]}_{parts2[7]}/{parts1[5]}_{parts1[2]}"


            # result = [products[picture]['generationdate'], products[picture]['title'],
            #           picture, preview, download]
            pictures.append(
                PictureModel(date=products[picture]['generationdate'], name=products[picture]['title'],
                             uuid=picture, prev=preview, download=download)
            )
        return pictures

    def down_url(self, uuid, ident, some_ident, img_ident):

        path = f"https://scihub.copernicus.eu/dhus/odata/v1/Products('{uuid}')/Nodes('{ident}.SAFE')/Nodes('GRANULE')\
/Nodes('{some_ident}')/Nodes('IMG_DATA')/Nodes('R10m')/Nodes('{img_ident}_TCI_10m.jp2')/$value"

        resp = self.api.session.get(f'{path}')

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)

        photo = response.data

        gdal.FileFromMemBuffer('/vsimem/inmem.jp2', photo)
        ds = gdal.Open('/vsimem/inmem.jp2')

        warp = gdal.Warp('/vsimem/inmem_3857.jp2', ds, dstSRS='EPSG:3857', outputType=gdal.gdalconst.GDT_Byte)
        warp = None

        ds1 = gdal.Translate(f'{uuid}.tif', '/vsimem/inmem_3857.jp2')
        print(ds1.GetMetadata())
        ds = None
        ds1 = None

        gdal.Unlink('/vsimem/inmem.jp2')
        gdal.Unlink('/vsimem/inmem_3857.jp2')

        return response

    def get_preview(self, uuid):

        path = f"https://scihub.copernicus.eu/dhus/odata/v1/Products('{uuid}')/Products('Quicklook')/$value"

        resp = self.api.session.get(path)

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response

    def create_picture(self, **kwargs) -> PictureModel:
        pass

    # def in_polygon(request):
    #     if request.method == 'POST':
    #         data = json.loads(request.body)
    #         in_polygon = False
    #
    #         # Main algorithms
    #         x = data['point'][0]
    #         y = data['point'][1]
    #         for i in range(len(data['polygon'])):
    #             xp = data['polygon'][i][0]
    #             yp = data['polygon'][i][1]
    #             xp_prev = data['polygon'][i - 1][0]
    #             yp_prev = data['polygon'][i - 1][1]
    #             if (((yp <= y and y < yp_prev) or (yp_prev <= y and y < yp)) and (
    #                     x > (xp_prev - xp) * (y - yp) / (yp_prev - yp) + xp)):
    #                 in_polygon = not in_polygon