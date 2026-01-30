
from flask import Blueprint, current_app

serve_static = Blueprint('serve_static', __name__)

@serve_static.route('/api/v2/_xx_/static/<path:filename>', methods=['OPTIONS', 'HEAD', 'GET'])
def serve_static():
    return current_app.view_functions['serve_static']()
