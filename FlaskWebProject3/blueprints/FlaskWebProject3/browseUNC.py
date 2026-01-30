
from flask import Blueprint, current_app

browseUNC = Blueprint('browseUNC', __name__)

@browseUNC.route('/api/v2/_xx_/api/browseUNC', methods=['POST', 'OPTIONS'])
def browseUNC():
    return current_app.view_functions['browseUNC']()
