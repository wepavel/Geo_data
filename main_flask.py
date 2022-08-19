from flask import Flask, request, redirect, Response
import requests
from sentinelsat.sentinel import SentinelAPI
import flask
import os

from model import PictureFabric
# import geopandas as gpd

import osgeo
from osgeo import gdal

app = Flask(__name__)


@app.route('/')
def index():
    return 'Flask is running!'


@app.route('/preview/<path:uuid>', methods=['GET'])
def prev_proxy(uuid):
    if request.method == 'GET':

        response = PictureFabric().get_preview(uuid)

        return response


@app.route('/download/<path:uuid>/<path:ident>/<path:some_ident>/<path:img_ident>', methods=['GET'])
def download_proxy(uuid, ident, some_ident, img_ident):
    print(uuid, ident, some_ident, img_ident)

    url = PictureFabric().down_url(uuid, ident, some_ident, img_ident)
    photo = url.data

    gdal.FileFromMemBuffer('/vsimem/inmem.vrt', photo)
    ds = gdal.Open('/vsimem/inmem.vrt')

    # print(ds.ReadAsArray().shape)
    # ds = None
    ds1 = gdal.Translate(f'/vsimem/{uuid}.tif', ds)

    data_array = ds1.GetMetadata()

    url.data = data_array
    url.response = data_array
    # gdal.GetDriverByName('tiff').CreateCopy(f'/vsimem/{uuid}.png', ds)
    ds = None
    gdal.Unlink('/vsimem/inmem.vrt')
    gdal.Unlink(f'/vsimem/{uuid}.tif')
    # ds = gdal.Open(photo)

    return url

@app.post('/regions')
def check_regions():
    pictures = PictureFabric().get_pictures(**flask.request.json)
    # xxx = flask.request.json
    # gdf = gpd.GeoDataFrame.from_features(xxx["features"])
    # pass
    # photos = PictureFabric().get_pictures(**flask.request.json)
    # return flask.jsonify(edited_user.to_dict())
    return flask.jsonify([picture.to_dict() for picture in pictures])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1060)

