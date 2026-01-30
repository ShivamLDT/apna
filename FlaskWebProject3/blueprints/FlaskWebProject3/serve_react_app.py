
from flask import Blueprint, current_app

serve_react_app = Blueprint('serve_react_app', __name__)

@serve_react_app.route('/api/v2/_xx_/<path:path>', methods=['OPTIONS', 'HEAD', 'GET'])
def serve_react_app():
    return current_app.view_functions['serve_react_app']()
