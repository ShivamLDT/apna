
from flask import Blueprint, current_app

contact = Blueprint('contact', __name__)

@contact.route('/api/v2/_xx_/contact', methods=['OPTIONS', 'HEAD', 'GET'])
def contact():
    return current_app.view_functions['contact']()
