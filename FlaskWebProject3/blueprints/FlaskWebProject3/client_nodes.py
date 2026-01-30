
from flask import Blueprint, current_app

client_nodes = Blueprint('client_nodes', __name__)

@client_nodes.route('/api/v2/_xx_/clientnodes', methods=['OPTIONS', 'HEAD', 'GET'])
def client_nodes():
    return current_app.view_functions['client_nodes']()
