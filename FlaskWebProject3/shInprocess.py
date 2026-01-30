import asyncio
from datetime  import datetime 
import multiprocessing
import os
import subprocess  # Add this import line
from apscheduler.schedulers.background import BackgroundScheduler

class TaskScheduler:
    def __init__(self, task_queue, result_queue):
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.scheduler = BackgroundScheduler()

    async def execute_task(self, job_id, executable_path):
        try:
            process = await asyncio.create_subprocess_shell(
                executable_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )

            stdout, stderr = await process.communicate()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if process.returncode == 0:
                print(f"Task {job_id} completed successfully. {current_time}")
                return True
            else:
                print(f"Task {job_id} failed with error: {stderr.decode()} {current_time}")
                return False

        except Exception as e:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Error executing task {job_id}: {str(e)} at {current_time} ")
            return False

    async def process_task(self, job):
        job_id, executable_path, interval, units = job

        while True:
            await asyncio.sleep(interval)
            status = await self.execute_task(job_id, executable_path)
            result = {'job_id': job_id, 'status': status}
            self.result_queue.send(result)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if status:
                print(f"Job {job_id} completed successfully. at {current_time}")
            else:
                print(f"Job {job_id} failed. at {current_time}" )

    def cleanup(self):
        # Cleanup resources
        self.scheduler.shutdown()

def worker_process(task_queue, result_queue):
    scheduler_instance = TaskScheduler(task_queue, result_queue)

    try:
        while True:
            job = task_queue.recv()
            if job == ('exit', ''):
                break

            asyncio.run(scheduler_instance.process_task(job))

    finally:
        # Clean up resources
        scheduler_instance.cleanup()

def main():
    # Create pipes for communication with worker processes
    task_pipes = [multiprocessing.Pipe() for _ in range(num_processes)]
    result_pipes = [multiprocessing.Pipe() for _ in range(num_processes)]

    # Start worker processes
    processes = []
    for i in range(num_processes):
        task_pipe_main, task_pipe_worker = task_pipes[i]
        result_pipe_worker, result_pipe_main = result_pipes[i]

        process = multiprocessing.Process(target=worker_process, args=(task_pipe_worker, result_pipe_main))
        process.start()
        processes.append(process)

    try:
        while True:
            job_id, executable_path, interval, units = input("Enter Job ID, Executable Path, Interval, and Units (seconds, minutes, hours, daily, weekly, monthly, yearly), or 'exit' to quit: ").split(",")

            if job_id.lower() == 'exit':
                break

            # Distribute tasks among worker processes
            task_pipes[0][0].send((int(job_id), executable_path, int(interval), units))

    finally:
        # Signal worker processes to exit
        for i in range(num_processes):
            task_pipes[i][0].send(('exit', ''))

        # Wait for worker processes to finish
        for process in processes:
            process.join()

if __name__ == "__main__":
    num_processes = multiprocessing.cpu_count()
    main()
