from flask import Flask, request, send_from_directory
import requests
from sentinelsat.sentinel import SentinelAPI
import flask


from model import PictureFabric


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

    someobject = PictureFabric().get_picture(uuid, ident, some_ident, img_ident)

    return someobject


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

