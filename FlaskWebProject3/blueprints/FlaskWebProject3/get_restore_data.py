
from flask import Blueprint, current_app

get_restore_data = Blueprint('get_restore_data', __name__)

@get_restore_data.route('/api/v2/_xx_/restore', methods=['POST', 'OPTIONS'])
def get_restore_data():
    return current_app.view_functions['get_restore_data']()
