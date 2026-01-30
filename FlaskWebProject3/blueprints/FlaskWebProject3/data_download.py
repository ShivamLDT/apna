
from flask import Blueprint, current_app

data_download = Blueprint('data_download', __name__)

@data_download.route('/api/v2/_xx_/data/download', methods=['POST', 'OPTIONS', 'HEAD', 'GET'])
def data_download():
    return current_app.view_functions['data_download']()
