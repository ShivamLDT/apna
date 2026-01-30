
from flask import Blueprint, current_app

live_data.live_data_view = Blueprint('live_data.live_data_view', __name__)

@live_data.live_data_view.route('/api/v2/_xx_/live_data/stream', methods=['OPTIONS', 'HEAD', 'GET'])
def live_data.live_data_view():
    return current_app.view_functions['live_data.live_data_view']()
