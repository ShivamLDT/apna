
# app/shared_data.py
from queue import Queue
import queue

notifications = queue.Queue(0)
notifications.put("hi")
