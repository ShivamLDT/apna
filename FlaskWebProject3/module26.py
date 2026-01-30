import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import logging

# Set up logging to capture job events
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def func1():
    # Your scheduled function logic goes here
    print("=======================================")
    print("Executing func1() at " + str(time.asctime()))
    time.sleep(8)
    print ("Executing func1() finished at " +str(time.asctime()))
    print("=======================================")
    print("\n\n")
    # Simulate success or failure as needed
    # Example: raise Exception("Failed!") to simulate a failure

# Event listener to track successful execution
def job_success(event):
    print("\n\n+++++++++++++++++++++++++++++++++++")
    print (str(time.asctime()))
    print("+++++++++++++++++++++++++++++++++++\n\n")
    job_id = event.job_id
    logger.info(f"Job {job_id} completed successfully.")

# Event listener to track failed execution
def job_failure(event):
    job_id = event.job_id
    logger.error(f"Job {job_id} failed with error: {event.exception}")
    print (str(datetime.datetime.time()))

# Initialize the scheduler
scheduler = BackgroundScheduler()

# Add job to scheduler
scheduler.add_job(func1, 'interval', seconds=10, id='n1')  # Schedule as needed

# Add listeners for job success and failure events
scheduler.add_listener(job_success, EVENT_JOB_EXECUTED)
scheduler.add_listener(job_failure, EVENT_JOB_ERROR)

# Start the scheduler
scheduler.start()
# Keep the script running to allow scheduler to execute jobs
try:
    # Run indefinitely to allow scheduled jobs to execute
    print("Scheduler started. Press Ctrl+C to exit.")
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    # Shut down the scheduler gracefully on exit
    scheduler.shutdown()
    print("Scheduler stopped.")

