
from flask import Blueprint, current_app

GetSchedulers = Blueprint('GetSchedulers', __name__)

@GetSchedulers.route('/api/v2/_xx_/schedulera', methods=['POST', 'OPTIONS', 'HEAD', 'GET'])
def GetSchedulers():
    return current_app.view_functions['GetSchedulers']()
