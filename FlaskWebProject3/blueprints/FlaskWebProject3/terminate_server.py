
from flask import Blueprint, current_app

terminate_server = Blueprint('terminate_server', __name__)

@terminate_server.route('/api/v2/_xx_/terminate', methods=['POST', 'OPTIONS'])
def terminate_server():
    return current_app.view_functions['terminate_server']()
