
from flask import Blueprint, current_app

browseNode = Blueprint('browseNode', __name__)

@browseNode.route('/api/v2/_xx_/api/browse', methods=['POST', 'OPTIONS'])
def browseNode():
    return current_app.view_functions['browseNode']()
