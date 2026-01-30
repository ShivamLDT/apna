
from flask import Blueprint, current_app

check_download = Blueprint('check_download', __name__)

@check_download.route('/api/v2/_xx_/agent/checkdownload', methods=['POST', 'OPTIONS', 'HEAD', 'GET'])
def check_download():
    return current_app.view_functions['check_download']()
