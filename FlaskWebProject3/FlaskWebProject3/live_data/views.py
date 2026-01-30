
# live_data/views.py
from flask import Blueprint, Response
import requests

live_data_bp = Blueprint("live_data", __name__, url_prefix="/live_data")


class LiveDataStream:
    def __call__(self):
        def event_stream():
            while True:
                response = requests.get("https://api.example.com/live-data")
                yield f"data: {response.json()}\n\n"

        return Response(event_stream(), mimetype="text/event-stream")


#live_data_view = LiveDataStream()  # LiveDataStream.as_view('live_data_stream')
def live_data_view():
    return LiveDataStream()  # LiveDataStream.as_view('live_data_stream')
live_data_bp.add_url_rule("/stream", view_func=live_data_view)
