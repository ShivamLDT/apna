
from flask import Blueprint, current_app

success_jobs = Blueprint('success_jobs', __name__)

@success_jobs.route('/api/v2/_xx_/api/getsuccessjobs', methods=['POST', 'OPTIONS', 'HEAD', 'GET'])
def success_jobs():
    return current_app.view_functions['success_jobs']()
