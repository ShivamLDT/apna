import threading
import time
import tracemalloc
from datetime import datetime
import sys
import os
sys.stdout = open("monitor_log.txt", "a", buffering=1)
sys.stderr = sys.stdout
class AppMonitor:
    def __init__(self, task_queue=None, interval=10, memory_frames=10, filter_filename=None):
        """
        task_queue: Optional queue.Queue to monitor
        interval: How often to log stats (seconds)
        memory_frames: Number of frames tracemalloc keeps
        filter_filename: Only show memory growth from this file (optional)
        """
        self.task_queue = task_queue
        self.interval = interval
        self.filter_filename = filter_filename
        self._stop_event = threading.Event()
        tracemalloc.start(memory_frames)
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()

 
    def _monitor(self):
        prev_snapshot = tracemalloc.take_snapshot()
        exclude_paths = [
            os.path.join(os.path.sep, "env"),  # Python stdlib
            os.path.join(os.path.sep, "lib", "python"),  # Python stdlib
            os.path.join(os.path.sep, "site-packages")  # third-party packages
        ]
        
        while not self._stop_event.is_set():
            time.sleep(self.interval)

            # 1 Thread count
            print(f"[Monitor  {str(datetime.now())}] Active threads: {len(threading.enumerate())}")

            # 2 Queue size
            if self.task_queue:
                print(f"[Monitor  {str(datetime.now())}] Queue size: {self.task_queue.qsize()}")

            # 3 Memory growth
            curr_snapshot = tracemalloc.take_snapshot()
            top_stats = curr_snapshot.compare_to(prev_snapshot, 'lineno')[:10]  # top 10
            if self.filter_filename:
                #top_stats = [s for s in top_stats if self.filter_filename in str(s)]

                top_stats = [
                    stat for stat in curr_snapshot.statistics('lineno')
                    if not any(excl in str(stat) for excl in exclude_paths)
                ]

            print(f"[Monitor {str(datetime.now())}] Top memory growth:")
            print("=================================================================================================")
            for stat in top_stats:
                print(f"{str(datetime.now())} {stat}")
                print("=================================================================================================")
            prev_snapshot = curr_snapshot

    def stop(self):
        self._stop_event.set()
        self.thread.join(timeout=2)
