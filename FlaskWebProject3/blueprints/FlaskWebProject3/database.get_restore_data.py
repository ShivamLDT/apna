
from flask import Blueprint, current_app

database.get_restore_data = Blueprint('database.get_restore_data', __name__)

@database.get_restore_data.route('/api/v2/_xx_/restore', methods=['POST', 'OPTIONS'])
def database.get_restore_data():
    return current_app.view_functions['database.get_restore_data']()
