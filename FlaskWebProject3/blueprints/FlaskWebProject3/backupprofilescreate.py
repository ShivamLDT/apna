
from flask import Blueprint, current_app

backupprofilescreate = Blueprint('backupprofilescreate', __name__)

@backupprofilescreate.route('/api/v2/_xx_/backupprofilescreate', methods=['POST', 'OPTIONS'])
def backupprofilescreate():
    return current_app.view_functions['backupprofilescreate']()
