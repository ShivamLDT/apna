# from flask import Flask, jsonify, request
# from flask_cors import CORS
# import json

# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

# def generate_backup_data():
#     backup_jobs = [
#         # {  
#         #     "name": "Backup Job 1",
#         #     "scheduled_time": "10:00:00",
#         #     "agent": "Agent1",
#         #     "progress_number": 25
#         # },
#         # {  
#         #     "name": "Backup Job 22",
#         #     "scheduled_time": "10:00:00",
#         #     "agent": "Agent1",
#         #     "progress_number": 40
#         # },
#         # {  
#         #     "name": "Backup Job 02",
#         #     "scheduled_time": "10:00:00",
#         #     "agent": "Agent1",
#         #     "progress_number": 70
#         # },
#         # {  
#         #     "name": "Backup Job 1",
#         #     "scheduled_time": "10:00:00",
#         #     "agent": "Agent1",
#         #     "progress_number": 50
#         # },
#         {  
#             "name": "Backup Job 91",
#             "scheduled_time": "10:00:00",
#             "agent": "Agent1",
#             "progress_number": 100
#         },
#         {
#             "name": "Backup Job 1",
#             "scheduled_time": "11:30:00",
#             "agent": "Agent1",
#             "progress_number": 50
#         },
#         {
#             "name": "Backup Jobs 1",
#             "scheduled_time": "12:30:00",
#             "agent": "Agent1",
#             "progress_number": 80
#         },
        
#         {
#             "name": "APna Backup",
#             "scheduled_time": "15:00:00",
#             "agent": "Agent2",
#             "progress_number": 70
#         },
#         {
#             "name": "APnaTally",
#             "scheduled_time": "18:00:00",
#             "agent": "Agent2",
#             "progress_number": 90
#         },
#         {
#             "name": "Backup Job 3",
#             "scheduled_time": "14:00:00",
#             "agent": "Agent3",
#             "progress_number": 75
#         },
#         {
#             "name": "Backup Job 4",
#             "scheduled_time": "14:00:00",
#             "agent": "Agent5",
#             "progress_number": 33
#         },
        
#         {
#             "name": "Jobio4",
#             "scheduled_time": "18:00:00",
#             "agent": "Agent5",
#             "progress_number": 68
#         }
#     ]
#     return jsonify({"backup_jobs": backup_jobs})

# @app.route('/api/backup_jobs', methods=['POST'])
# def get_backup_data():
#     # Optionally handle request data if needed
#     request_data = request.get_json()  # Get JSON data from the request
#     # For example, you could process the data here

#     return generate_backup_data()

# # if __name__ == '__main__':
# #       app.run(debug=True, port=8000)

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=8000)


#random
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# import json
# import random
# from datetime import datetime, timedelta

# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

# def generate_backup_data():
#     agents = ["Agent1", "Agent2", "Agent3", "Agent4", "Agent5"]
#     job_names = ["Backup Job 1", "Backup Job 2", "Backup Job 3", "Backup Job 4", "Backup Job 5"]
#     scheduled_times = [f"{hour:02}:{minute:02}:00" for hour in range(8, 18) for minute in range(0, 60, 30)]

#     backup_jobs = []

#     # Generate jobs for each agent
#     for agent in agents:
#         for _ in range(random.randint(5, 10)):  # Random number of jobs per agent
#             job = {
#                 "name": random.choice(job_names),
#                 "scheduled_time": random.choice(scheduled_times),
#                 "agent": agent,
#                 "progress_number": random.randint(0, 100)
#             }
#             backup_jobs.append(job)

#     # Generate jobs for overlapping times for the same agent
#     for agent in agents:
#         # Randomly generate overlapping jobs
#         for _ in range(random.randint(2, 5)):
#             job = {
#                 "name": random.choice(job_names),
#                 "scheduled_time": random.choice(scheduled_times),
#                 "agent": agent,
#                 "progress_number": random.randint(0, 100)
#             }
#             backup_jobs.append(job)

#     return jsonify({"backup_jobs": backup_jobs})

# @app.route('/api/backup_jobs', methods=['POST'])
# def get_backup_data():
#     request_data = request.get_json()  # Get JSON data from the request
#     # For example, you could process the data here
#     return generate_backup_data()

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=8000)


# get

# from flask import Flask, jsonify, request
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

# def generate_backup_data():
#     backup_jobs = [
        # {  
        #     "name": "Backup Job 1",
        #     "scheduled_time": "10:00:00",
        #     "agent": "Agent1",
        #     "progress_number": 25
        # },
        # {  
        #     "name": "Backup Job 22",
        #     "scheduled_time": "10:00:00",
        #     "agent": "Agent1",
        #     "progress_number": 40
        # },
        # {  
        #     "name": "Backup Job 02",
        #     "scheduled_time": "10:00:00",
        #     "agent": "Agent1",
        #     "progress_number": 70
        # },
        # {  
        #     "name": "Backup Job 2",
        #     "scheduled_time": "12:00:00",
        #     "agent": "Agent1",
        #     "progress_number": 80
        # },
        # {  
        #     "name": "Tally 2",
        #     "scheduled_time": "18:00:00",
        #     "agent": "Agent1",
        #     "progress_number": 70
        # },
        # {  
        #     "name": "Backup Job 1",
        #     "scheduled_time": "10:00:00",
        #     "agent": "Agent1",
        #     "progress_number": 50
        # },
        # {  
        #     "name": "Backup Job 1",
        #     "scheduled_time": "10:00:00",
        #     "agent": "Agent1",
        #     "progress_number": 100
        # },
        # {
        #     "name": "Backup Job 2",
        #     "scheduled_time": "10:30:00",
        #     "agent": "Agent1",
        #     "progress_number": 40
        # },
        # {
        #     "name": "Backup Job 1",
        #     "scheduled_time": "10:30:00",
        #     "agent": "Agent1",
        #     "progress_number": 50
        # },
        # {
        #     "name": "Backup Job 2",
        #     "scheduled_time": "12:00:00",
        #     "agent": "Agent2",
        #     "progress_number": 50
        # },
        
        # {
        #     "name": "APna Backup",
        #     "scheduled_time": "15:00:00",
        #     "agent": "Agent2",
        #     "progress_number": 70
        # },
        # {
        #     "name": "Backup Job 3",
        #     "scheduled_time": "14:00:00",
        #     "agent": "Agent3",
        #     "progress_number": 75
        # },
        # {
        #     "name": "Backup Job 4",
        #     "scheduled_time": "14:00:00",
        #     "agent": "Agent5",
        #     "progress_number": 33
        # },
        
        # {
        #     "name": "Job4",
        #     "scheduled_time": "18:00:00",
        #     "agent": "Agent5",
        #     "progress_number": 68
        # }
#     ]
#     return jsonify({"backup_jobs": backup_jobs})

# @app.route('/api/backup_jobs', methods=['GET'])
# def get_backup_data():
#     # For GET requests, you generally don't need to handle request data
#     # You can use request.args to handle query parameters if needed
#     # For example: request.args.get('param_name')
    
#     return generate_backup_data()

# if __name__ == '__main__':
#     app.run(debug=True, port=8000)




#websocket
# from flask import Flask
# from flask_socketio import SocketIO, emit

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'mysecret'
# socketio = SocketIO(app, cors_allowed_origins="*")

# def generate_backup_data():
#     # Example data for demonstration
#     return {
#         "backup_jobs": [
#             {"name": "Backup Job 1", "scheduled_time": "10:00:00", "agent": "Agent1", "progress_number": 25},
#             {"name": "Backup Job 2", "scheduled_time": "12:00:00", "agent": "Agent1", "progress_number": 85},
#             {"name": "Backup Job 3", "scheduled_time": "14:00:00", "agent": "Agent2", "progress_number": 50},
#             {"name": "Backup Job 31", "scheduled_time": "14:00:00", "agent": "Agent2", "progress_number": 50},
#         ]
#     }

# @socketio.on('request_backup_data')
# def handle_request_backup_data(data):
#     print("Event 'request_backup_data' triggered.")
#     print(f"Received data: {data}")

#     try:
#         backup_data = generate_backup_data()
#         emit('backup_data', backup_data)
#     except Exception as e:
#         print(f"Error sending backup data: {e}")

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=8000)



# from flask import Flask
# from flask_socketio import SocketIO, emit
# import time
# import threading
# import random

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'mysecret'
# socketio = SocketIO(app, cors_allowed_origins="*")

# # Example data
# backup_jobs = [
#     {"name": "Backup Job 1", "scheduled_time": "10:00:00", "agent": "Agent1", "progress_number": 25},

# ]

# def generate_backup_data():
#     # Simulate progress updates by randomizing progress numbers
#     updated_data = []
#     for job in backup_jobs:
#         updated_job = job.copy()
#         updated_job['progress_number'] = min(100, job['progress_number'] + random.randint(1, 5))  # Increment progress
#         updated_data.append(updated_job)
#     return {"backup_jobs": updated_data}

# def send_progress_updates():
#     while True:
#         # Generate and emit backup data
#         backup_data = generate_backup_data()
#         socketio.emit('backup_data', backup_data)
#         print("Sent backup data:", backup_data)
#         time.sleep(1)  # Send updates every 1 second

# @socketio.on('request_backup_data')
# def handle_request_backup_data(data):
#     print("Event 'request_backup_data' triggered.")
#     print(f"Received data: {data}")

#     try:
#         # Start the background task to send progress updates
#         if not hasattr(handle_request_backup_data, 'thread'):
#             thread = threading.Thread(target=send_progress_updates)
#             thread.daemon = True
#             thread.start()
#             handle_request_backup_data.thread = thread
#         else:
#             print("Progress update thread is already running.")
#     except Exception as e:
#         print(f"Error starting progress update thread: {e}")

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=8000)


# from flask import Flask
# from flask_socketio import SocketIO
# import time
# import threading
# import random

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'mysecret'
# socketio = SocketIO(app, cors_allowed_origins="*")

# # Example data with 20 different jobs
# backup_jobs = [
#     {"name": f"Backup Job {i}", "scheduled_time": "10:00:00", "agent": f"Agent{i}", "progress_number": random.randint(0, 10)}
#     for i in range(1, 21)
# ]

# # Store the previous state of each job
# previous_backup_jobs = {job['agent']: job.copy() for job in backup_jobs}

# def generate_backup_data():
#     updated_job = None
#     for job in backup_jobs:
#         previous_job = previous_backup_jobs[job['agent']]
#         new_progress = min(100, job['progress_number'] + random.randint(1, 5))  # Increment progress
#         if new_progress != previous_job['progress_number']:
#             updated_job = job.copy()  # Capture the updated job
#             updated_job['progress_number'] = new_progress
#             # Update the previous job state
#             previous_backup_jobs[job['agent']] = updated_job
#             break  # Only send one updated job at a time

#     # If no job is updated, return None to indicate no changes
#     return updated_job

# def send_progress_updates():
#     while True:
#         # Generate and emit backup data
#         updated_job = generate_backup_data()
#         if updated_job:  # Emit only if there is an updated job
#             socketio.emit('backup_data', {"backup_jobs": [updated_job]})
#             print("Sent backup data:", {"backup_jobs": [updated_job]})  # Debug print to verify data
#         time.sleep(1)  # Send updates every 1 second

# @socketio.on('request_backup_data')
# def handle_request_backup_data(data):
#     print("Event 'request_backup_data' triggered.")
#     print(f"Received data: {data}")

#     try:
#         # Start the background task to send progress updates
#         if not hasattr(handle_request_backup_data, 'thread'):
#             thread = threading.Thread(target=send_progress_updates)
#             thread.daemon = True
#             thread.start()
#             handle_request_backup_data.thread = thread
#         else:
#             print("Progress update thread is already running.")
#     except Exception as e:
#         print(f"Error starting progress update thread: {e}")

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=8000)

from flask import Flask
from flask_socketio import SocketIO
import time
import threading
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Example data with multiple jobs per agent at different times
backup_jobs = [
    # Jobs for Agent A
    {"name": f"Backup Job {i}", "scheduled_time": f"10:{i:02}:00", "agent": "AgentA", "progress_number": random.randint(0, 100)}
    for i in range(1, 6)
] + [
    {"name": f"Backup Job {i+5}", "scheduled_time": f"12:{i:02}:00", "agent": "AgentA", "progress_number": random.randint(0, 100)}
    for i in range(1, 4)
] + [
    {"name": f"Backup Job {i+8}", "scheduled_time": f"11:{i:02}:00", "agent": "AgentA", "progress_number": random.randint(0, 100)}
    for i in range(1, 7)
] + [
    # Jobs for Agent B
    {"name": f"Backup Job {i+14}", "scheduled_time": f"15:{i:02}:00", "agent": "AgentB", "progress_number": random.randint(0, 100)}
    for i in range(1, 6)
] + [
    {"name": f"Backup Job {i+19}", "scheduled_time": f"19:{i:02}:00", "agent": "AgentB", "progress_number": random.randint(0, 100)}
    for i in range(1, 4)
] + [
    {"name": f"Backup Job {i+22}", "scheduled_time": f"18:{i:02}:00", "agent": "AgentB", "progress_number": random.randint(0, 100)}
    for i in range(1, 7)
]

# Store the previous state of each job
previous_backup_jobs = {job['agent']: {} for job in backup_jobs}
for job in backup_jobs:
    previous_backup_jobs[job['agent']][job['name']] = job.copy()

def generate_backup_data():
    updated_jobs = []
    for job in backup_jobs:
        # Simulate progress updates at random intervals
        if random.random() < 0.1:  # 10% chance to update a job
            previous_jobs = previous_backup_jobs[job['agent']]
            previous_job = previous_jobs.get(job['name'])
            if previous_job:
                new_progress = min(100, previous_job['progress_number'] + random.randint(1, 5))  # Increment progress
                if new_progress != previous_job['progress_number']:
                    updated_job = job.copy()  # Capture the updated job
                    updated_job['progress_number'] = new_progress
                    # Update the previous job state
                    previous_backup_jobs[job['agent']][job['name']] = updated_job
                    updated_jobs.append(updated_job)
    return updated_jobs

def send_progress_updates():
    while True:
        updated_jobs = generate_backup_data()
        if updated_jobs:  # Emit only if there are updated jobs
            socketio.emit('backup_data', {"backup_jobs": updated_jobs})
            print("Sent backup data:", {"backup_jobs": updated_jobs})  # Debug print to verify data
        time.sleep(1)  # Check for updates every 1 second

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
