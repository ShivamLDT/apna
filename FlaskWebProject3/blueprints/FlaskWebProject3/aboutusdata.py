
from flask import Blueprint, current_app

aboutusdata = Blueprint('aboutusdata', __name__)

@aboutusdata.route('/api/v2/_xx_/aboutusdata', methods=['OPTIONS', 'HEAD', 'GET'])
def aboutusdata():
    return current_app.view_functions['aboutusdata']()
