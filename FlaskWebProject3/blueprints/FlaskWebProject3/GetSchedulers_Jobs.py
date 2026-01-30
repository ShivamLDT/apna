
from flask import Blueprint, current_app

GetSchedulers_Jobs = Blueprint('GetSchedulers_Jobs', __name__)

@GetSchedulers_Jobs.route('/api/v2/_xx_/scheduler', methods=['POST', 'OPTIONS', 'HEAD', 'GET'])
def GetSchedulers_Jobs():
    return current_app.view_functions['GetSchedulers_Jobs']()
