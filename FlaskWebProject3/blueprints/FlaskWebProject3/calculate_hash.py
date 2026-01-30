
from flask import Blueprint, current_app

calculate_hash = Blueprint('calculate_hash', __name__)

@calculate_hash.route('/api/v2/_xx_/api/calculatehash', methods=['POST', 'OPTIONS'])
def calculate_hash():
    return current_app.view_functions['calculate_hash']()
