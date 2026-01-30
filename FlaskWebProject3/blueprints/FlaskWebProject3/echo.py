
from flask import Blueprint, current_app

echo = Blueprint('echo', __name__)

@echo.route('/api/v2/_xx_/echo', methods=['OPTIONS', 'HEAD', 'GET'])
def echo():
    return current_app.view_functions['echo']()
