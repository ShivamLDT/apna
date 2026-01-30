
from flask import Blueprint, current_app

notifications.notifications_view = Blueprint('notifications.notifications_view', __name__)

@notifications.notifications_view.route('/api/v2/_xx_/notifications/stream', methods=['OPTIONS', 'HEAD', 'GET'])
def notifications.notifications_view():
    return current_app.view_functions['notifications.notifications_view']()
