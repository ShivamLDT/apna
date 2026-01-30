
from flask import Blueprint, current_app

go_up = Blueprint('go_up', __name__)

@go_up.route('/api/v2/_xx_/api/go-up', methods=['POST', 'OPTIONS'])
def go_up():
    return current_app.view_functions['go_up']()
