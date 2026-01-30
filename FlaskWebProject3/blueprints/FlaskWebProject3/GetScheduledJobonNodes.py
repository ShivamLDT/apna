
from flask import Blueprint, current_app

GetScheduledJobonNodes = Blueprint('GetScheduledJobonNodes', __name__)

@GetScheduledJobonNodes.route('/api/v2/_xx_/scheduler/jobs', methods=['POST', 'OPTIONS', 'HEAD', 'GET'])
def GetScheduledJobonNodes():
    return current_app.view_functions['GetScheduledJobonNodes']()
