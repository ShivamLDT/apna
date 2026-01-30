
from flask import Blueprint, current_app

send_simple_message = Blueprint('send_simple_message', __name__)

@send_simple_message.route('/api/v2/_xx_/sendemail', methods=['OPTIONS', 'HEAD', 'GET'])
def send_simple_message():
    return current_app.view_functions['send_simple_message']()
