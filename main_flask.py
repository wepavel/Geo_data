# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from flask import Flask, request
import flask

from model import ImageFabric

app = Flask(__name__)


@app.route('/')
def index():
    return 'Flask is running!'


@app.get('/preview/<path:uuid>')
def prev_proxy(uuid):
    """Get preview of chosen image"""
    if request.method == 'GET':
        prev_resp = ImageFabric().get_preview(uuid)

        return prev_resp


@app.get('/download/<path:uuid>/<path:ident>/<path:some_ident>/<path:img_ident>')
def download_proxy(uuid, ident, some_ident, img_ident):
    """Download image in .tif in EPSG:3857 projection"""
    print(uuid, ident, some_ident, img_ident)

    img_resp = ImageFabric().get_image(uuid, ident, some_ident, img_ident)

    return img_resp


@app.post('/regions')
def check_regions():
    """Check for available images in region"""
    img_models = ImageFabric().get_images(**flask.request.json)

    return flask.jsonify([image.to_dict() for image in img_models])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1060)
