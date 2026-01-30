
from flask import Blueprint, current_app

authen = Blueprint('authen', __name__)

@authen.route('/api/v2/_xx_/authen', methods=['OPTIONS', 'HEAD', 'GET'])
def authen():
    return current_app.view_functions['authen']()
