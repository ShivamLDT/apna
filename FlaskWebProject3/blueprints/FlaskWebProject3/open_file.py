
from flask import Blueprint, current_app

open_file = Blueprint('open_file', __name__)

@open_file.route('/api/v2/_xx_/api/open-file', methods=['POST', 'OPTIONS'])
def open_file():
    return current_app.view_functions['open_file']()
