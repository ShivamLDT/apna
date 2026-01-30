
from flask import Blueprint, current_app

home = Blueprint('home', __name__)

@home.route('/api/v2/_xx_/', methods=['OPTIONS', 'HEAD', 'GET'])
def home():
    return current_app.view_functions['home']()
