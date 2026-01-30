
# /notifications/views.py
 
from queue import Queue
import time
from flask import Blueprint, Response, request
from FlaskWebProject3.shared_data import notifications


# Define the blueprint
notifications_bp = Blueprint('notifications', __name__,url_prefix='/notifications')

class NotificationsStream:
    def __call__(self):
        def event_stream():
            while True:
                notification = notifications.get()
                if notification:
                    yield f'data: {notification}\n\n'
                else:
                    time.time.sleep(10)  # Introduce a small delay to avoid high CPU usage

        return Response(event_stream(), mimetype="text/event-stream")

# Create an instance of the NotificationsStream class
#notifications_view = NotificationsStream()
def notifications_view():
    
    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
    }
    def event_stream():
        while True:
            notification = notifications.get()
            if notification:
                yield f'data: {notification}\n\n'
                yield f': keep-alive\n\n'
            else:
                time.time.sleep(10)  # Introduce a small delay to avoid high CPU usage

    return Response(event_stream(), mimetype="text/event-stream",headers=headers)


@notifications_bp.route('/streamset', methods=['POST'])
def notifications_set():
    message = request.json
    try:
        if  notifications.qsize()<1: 
            notifications= Queue()
        notifications.put(str(message["message"]),timeout=20)
    #     if(message["message"]):
    #         notifications.put(message["message"])
    #         return 200
    except Exception as der:
        print(str(der))
            
    return 200


# Register the route with the blueprint
notifications_bp.add_url_rule('/stream', view_func=notifications_view)
