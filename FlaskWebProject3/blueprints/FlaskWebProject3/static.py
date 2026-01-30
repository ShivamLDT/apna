
from flask import Blueprint, current_app

static = Blueprint('static', __name__)

@static.route('/api/v2/_xx_/<path:filename>', methods=['OPTIONS', 'HEAD', 'GET'])
def static():
    return current_app.view_functions['static']()
