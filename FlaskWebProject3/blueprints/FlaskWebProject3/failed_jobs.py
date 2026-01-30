
from flask import Blueprint, current_app

failed_jobs = Blueprint('failed_jobs', __name__)

@failed_jobs.route('/api/v2/_xx_/api/getfailedjobs', methods=['POST', 'OPTIONS', 'HEAD', 'GET'])
def failed_jobs():
    return current_app.view_functions['failed_jobs']()
