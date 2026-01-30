
from flask import Blueprint, current_app

backup_jobs = Blueprint('backup_jobs', __name__)

@backup_jobs.route('/api/v2/_xx_/backupjobs', methods=['OPTIONS', 'HEAD', 'GET'])
def backup_jobs():
    return current_app.view_functions['backup_jobs']()
