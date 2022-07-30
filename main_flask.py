from flask import Flask,request,redirect,Response
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
def proxy(uuid):
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


@app.post('/regions')
def check_regions():
    pictures = PictureFabric().get_pictures(**flask.request.json)
    # xxx = flask.request.json
    # gdf = gpd.GeoDataFrame.from_features(xxx["features"])
    # pass
    # photos = PictureFabric().get_pictures(**flask.request.json)
    # return flask.jsonify(edited_user.to_dict())



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1060)
