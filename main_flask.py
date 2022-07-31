from flask import Flask, request, redirect, Response
import requests
from sentinelsat.sentinel import SentinelAPI
import flask
from flask import Flask

from model import PictureFabric
import geopandas as gpd


app = Flask(__name__)


@app.route('/')
def index():
    return 'Flask is running!'


@app.route('/preview/<path:uuid>', methods=['GET'])
def prev_proxy(uuid):
    if request.method == 'GET':

        user = 'wepaul'
        password = 'Sporopedu123'
        api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')
        path = f"https://scihub.copernicus.eu/dhus/odata/v1/Products('{uuid}')/Products('Quicklook')/$value"

        resp = api.session.get(f'{path}')

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
    return response

@app.route('/download/<path:uuid>', methods=['GET'])
def download_proxy(uuid):


    # https://scihub.copernicus.eu/dhus/odata/v1/Products('b246fb51-6c43-454a-bf49-385f5688bf63')/Nodes('S2B_MSIL2A_20220205T084039_N0400_R064_T37UCA_20220205T105847.SAFE')/Nodes('GRANULE')/Nodes('L2A_T37UCA_A025687_20220205T084305')/Nodes('IMG_DATA')/Nodes('R10m')/Nodes

    pass

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

