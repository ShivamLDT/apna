from flask import Flask
from flask_socketio import SocketIO
import time
import threading
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Limited backup jobs for two agents
backup_jobs = [
    {"name": "Backup Job 1", "scheduled_time": "10:01:00", "agent": "AgentA", 
     "progress_number": 100, "restore_flag": True,"path":"c:/folder/a.png"},  # Restore
    {"name": "Backup Job 2", "scheduled_time": "10:02:00", "agent": "AgentA", 
     "progress_number": 100, "restore_flag": True,"path":"c:/folder/a.png/abcd"},  # Restore
    {"name": "Backup Job 3", "scheduled_time": "10:03:00", "agent": "AgentA", 
     "progress_number": 100, "restore_flag": True,"path":"c:/folder/a.png/eef/oo"},  # Restore
    {"name": "Backup Job 4", "scheduled_time": "10:04:00", "agent": "AgentA", 
     "progress_number": 100, "restore_flag": True,"path":"c:/folder/a.png/op/po/op/po"},  # Restore
    {"name": "Backup Job 1", "scheduled_time": "10:01:00", "agent": "AgentB", 
     "progress_number": 0, "restore_flag": False,"path":"c:/folder/a.png"},  # Backup
    {"name": "Backup Job 2", "scheduled_time": "10:02:00", "agent": "AgentB", 
     "progress_number": 0, "restore_flag": False,"path":"c:/folder/a.png"},  # Backup
    {"name": "Backup Job 3", "scheduled_time": "10:03:00", "agent": "AgentB", 
     "progress_number": 0, "restore_flag": False,"path":"c:/folder/a.png"},  # Backup
    {"name": "Backup Job 4", "scheduled_time": "10:04:00", "agent": "AgentB", 
     "progress_number": 0, "restore_flag": False,"path":"c:/folder/a.png"},  # Backup
]

# Store the previous state of each job
previous_backup_jobs = {job['agent']: {} for job in backup_jobs}
for job in backup_jobs:
    previous_backup_jobs[job['agent']][job['name']] = job.copy()

def generate_backup_data(restore_flag):
    updated_jobs = []
    for job in backup_jobs:
        previous_jobs = previous_backup_jobs[job['agent']]
        previous_job = previous_jobs.get(job['name'])
        
        if job['restore_flag']:  # For AgentA
            if previous_job and previous_job['progress_number'] > 0:
                new_progress = max(0, previous_job['progress_number'] - random.randint(1, 5))
                if new_progress != previous_job['progress_number']:
                    updated_job = job.copy()
                    updated_job['progress_number'] = new_progress
                    previous_backup_jobs[job['agent']][job['name']] = updated_job
                    updated_jobs.append(updated_job)
            # Restart job if it reaches 0
            elif previous_job and previous_job['progress_number'] == 0:
                new_progress = 100  # Restart from 100
                updated_job = job.copy()
                updated_job['progress_number'] = new_progress
                previous_backup_jobs[job['agent']][job['name']] = updated_job
                updated_jobs.append(updated_job)

        else:  # For AgentB
            if previous_job and previous_job['progress_number'] < 100:
                new_progress = min(100, previous_job['progress_number'] + random.randint(1, 5))
                if new_progress != previous_job['progress_number']:
                    updated_job = job.copy()
                    updated_job['progress_number'] = new_progress
                    previous_backup_jobs[job['agent']][job['name']] = updated_job
                    updated_jobs.append(updated_job)
            # Restart job if it reaches 100
            elif previous_job and previous_job['progress_number'] == 100:
                new_progress = 0  # Restart from 0
                updated_job = job.copy()
                updated_job['progress_number'] = new_progress
                previous_backup_jobs[job['agent']][job['name']] = updated_job
                updated_jobs.append(updated_job)
    
    return updated_jobs

def send_progress_updates():
    while True:
        updated_jobs = generate_backup_data(restore_flag=True) + generate_backup_data(restore_flag=False)
        if updated_jobs:  # Emit only if there are updated jobs
            socketio.emit('backup_data', {"backup_jobs": updated_jobs})
            print("Sent backup data:", {"backup_jobs": updated_jobs})  # Debug print to verify data
        time.sleep(5)  # Check for updates every 6 seconds

@socketio.on('request_backup_data')
def handle_request_backup_data(data):
    print("Event 'request_backup_data' triggered.")
    print(f"Received data: {data}")

    try:
        # Start the background task to send progress updates
        if not hasattr(handle_request_backup_data, 'thread') or not handle_request_backup_data.thread.is_alive():
            thread = threading.Thread(target=send_progress_updates)
            thread.daemon = True
            thread.start()
            handle_request_backup_data.thread = thread
        else:
            print("Progress update thread is already running.")
    except Exception as e:
        print(f"Error starting progress update thread: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

