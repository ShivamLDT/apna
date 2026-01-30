import os
import asyncio
import multiprocessing
import subprocess
from jinja2.defaults import KEEP_TRAILING_NEWLINE
import schedule
import time
from apscheduler.schedulers.background import BackgroundScheduler

from fClient.fingerprint import get_miltiprocessing_cpu_count

class TaskScheduler:
    def __init__(self):
        self.task_queue = multiprocessing.Queue()
        self.processes = []
        self.scheduler = BackgroundScheduler()
        self.job_identifiers = set()
        self.load_schedule_from_file()

    def schedule_task(self, job_id, executable_path, interval, units):
        job_identifier = f"{job_id}_{units}_{interval}"
        
        if job_identifier in self.job_identifiers:
            print(f"Job {job_identifier} already scheduled.")
            return

        if units == 'seconds':
            self.scheduler.add_job(self.task_queue.put, 'interval', seconds=interval, args=[(job_id, executable_path)])
        elif units == 'minutes':
            self.scheduler.add_job(self.task_queue.put, 'interval', minutes=interval, args=[(job_id, executable_path)])
        elif units == 'hours':
            self.scheduler.add_job(self.task_queue.put, 'interval', hours=interval, args=[(job_id, executable_path)] )
        elif units == 'daily':
            self.scheduler.add_job(self.task_queue.put, 'interval', days=interval, args=[(job_id, executable_path)])
        elif units == 'weekly':
            self.scheduler.add_job(self.task_queue.put, 'interval', weeks=interval, args=[(job_id, executable_path)])
        elif units == 'monthly':
            self.scheduler.add_job(self.task_queue.put, 'cron', month='*', day=interval, args=[(job_id, executable_path)])
        elif units == 'yearly':
            self.scheduler.add_job(self.task_queue.put, 'cron', month='*', day=interval, args=[(job_id, executable_path)])

        self.job_identifiers.add(job_identifier)
        self.save_schedule_to_file()

    async def execute_task(self, job_id, executable_path):
        try:
            subprocess.run(executable_path, check=True)
            return True  # Task completed successfully
        except subprocess.CalledProcessError:
            return False  # Task failed

    async def worker(self):
        while True:
            job_id, executable_path = self.task_queue.get()
            status = await self.execute_task(job_id, executable_path)

            if status:
                print(f"Job {job_id} completed successfully.")
            else:
                print(f"Job {job_id} failed.")

    async def start_scheduler(self):
        # Start worker processes
        num_processes = get_miltiprocessing_cpu_count()
        for _ in range(num_processes):
            process = multiprocessing.Process(target=self.worker)
            process.start()
            self.processes.append(process)

        # Main loop to schedule tasks
        while True:
            job_id, executable_path, interval, units = input("Enter Job ID, Executable Path, Interval, and Units (seconds, minutes, hours, daily, weekly, monthly, yearly), or 'exit' to quit: ").split()

            if job_id.lower() == 'exit':
                break

            self.schedule_task(int(job_id), executable_path, int(interval), units)

        # Signal worker processes to exit
        for _ in range(num_processes):
            self.task_queue.put(('exit', ''))

        # Wait for worker processes to finish
        for process in self.processes:
            process.join()

    def save_schedule_to_file(self):
        with open('schedule.txt', 'w') as file:
            file.write('\n'.join(self.job_identifiers))

    def load_schedule_from_file(self):
        if os.path.exists('schedule.txt'):
            with open('schedule.txt', 'r') as file:
                lines = file.read().splitlines()
                self.job_identifiers = set(lines)

if __name__ == "__main__":
    scheduler = TaskScheduler()
    asyncio.run(scheduler.start_scheduler())

