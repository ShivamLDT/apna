
from flask import Blueprint, current_app

readdata = Blueprint('readdata', __name__)

@readdata.route('/api/v2/_xx_/get_restore_data', methods=['OPTIONS', 'HEAD', 'GET'])
def readdata():
    return current_app.view_functions['readdata']()
