
from flask import Blueprint, current_app

upload_file = Blueprint('upload_file', __name__)

@upload_file.route('/api/v2/_xx_/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    return current_app.view_functions['upload_file']()
