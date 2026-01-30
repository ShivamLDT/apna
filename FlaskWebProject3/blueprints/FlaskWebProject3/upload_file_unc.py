
from flask import Blueprint, current_app

upload_file_unc = Blueprint('upload_file_unc', __name__)

@upload_file_unc.route('/api/v2/_xx_/uploadunc', methods=['POST', 'OPTIONS'])
def upload_file_unc():
    return current_app.view_functions['upload_file_unc']()
