
from flask import Blueprint, current_app

tellme = Blueprint('tellme', __name__)

@tellme.route('/api/v2/_xx_/tellme', methods=['POST', 'OPTIONS', 'HEAD', 'GET'])
def tellme():
    return current_app.view_functions['tellme']()
