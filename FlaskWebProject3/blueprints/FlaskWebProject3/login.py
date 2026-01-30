
from flask import Blueprint, current_app

login = Blueprint('login', __name__)

@login.route('/api/v2/_xx_/login', methods=['POST', 'OPTIONS'])
def login():
    return current_app.view_functions['login']()
