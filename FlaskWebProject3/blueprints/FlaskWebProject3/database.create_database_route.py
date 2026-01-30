
from flask import Blueprint, current_app

database.create_database_route = Blueprint('database.create_database_route', __name__)

@database.create_database_route.route('/api/v2/_xx_/create_database', methods=['POST', 'OPTIONS'])
def database.create_database_route():
    return current_app.view_functions['database.create_database_route']()
