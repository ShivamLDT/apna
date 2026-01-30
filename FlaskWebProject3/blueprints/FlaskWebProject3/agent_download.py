
from flask import Blueprint, current_app

agent_download = Blueprint('agent_download', __name__)

@agent_download.route('/api/v2/_xx_/agent/download', methods=['POST', 'OPTIONS', 'HEAD', 'GET'])
def agent_download():
    return current_app.view_functions['agent_download']()
