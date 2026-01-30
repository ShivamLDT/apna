
from flask import Blueprint, current_app

notifications.notifications_set = Blueprint('notifications.notifications_set', __name__)

@notifications.notifications_set.route('/api/v2/_xx_/notifications/streamset', methods=['POST', 'OPTIONS'])
def notifications.notifications_set():
    return current_app.view_functions['notifications.notifications_set']()
