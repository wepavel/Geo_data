from flask import Flask, request, send_from_directory
import requests
from sentinelsat.sentinel import SentinelAPI
import flask
import os
import pickle

from model import PictureFabric
# import geopandas as gpd


import osgeo
from osgeo import gdal, gdal_array

import io

import sys

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

    dir, name = PictureFabric().down_url(uuid, ident, some_ident, img_ident)

    return send_from_directory(dir, name, as_attachment=True)

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

