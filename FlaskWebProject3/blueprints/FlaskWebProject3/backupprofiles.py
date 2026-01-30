
from flask import Blueprint, current_app

backupprofiles = Blueprint('backupprofiles', __name__)

@backupprofiles.route('/api/v2/_xx_/backupprofiles', methods=['POST', 'OPTIONS', 'HEAD', 'GET'])
def backupprofiles():
    return current_app.view_functions['backupprofiles']()
