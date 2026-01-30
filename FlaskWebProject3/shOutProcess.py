import asyncio
import multiprocessing
import os
import subprocess
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler 

class TaskScheduler:
    def __init__(self, task_queue, result_queue):
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.scheduler =  BackgroundScheduler() #AsyncIOScheduler() #
        #self.load_schedule_from_file()
        self.scheduler.add_job(
                self.process_task,
                'interval',
                seconds=35,
                kwargs={'job': ('2563', "ping icicibank.com -t -4", 35, "seconds")}
            )
       

    async def execute_task(self, job_id, executable_path):
        try:
            print(f'attempting \n{executable_path}')
            process = await asyncio.create_subprocess_shell(
                executable_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

            stdout, stderr = await process.communicate()
            if stdout:
                print(f'[stdout]\n{stdout.decode()}')
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if process.returncode == 0:                
                print(f"Task {job_id} completed successfully.{current_time}")
                return True
            else:
                print(f"Task {job_id} failed with error: {stderr.decode()}{current_time}")
                return False

        except Exception as e:
            print(f"Error executing task {job_id}: {str(e)} {current_time}")
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
                print(f"Job {job_id} completed successfully.{current_time}")
            else:
                print(f"Job {job_id} failed.{current_time}")

    def cleanup(self):
        # Cleanup resources
            self.scheduler.shutdown()
            loop = asyncio.get_event_loop()
            loop.stop()

    def load_schedule_from_file(self):
        if os.path.exists('schedule.txt'):
            with open('schedule.txt', 'r') as file:
                lines = file.read().splitlines()
                for line in lines:
                    job_id, executable_path, interval, units = line.split(',')
                    self.schedule_task(int(job_id), executable_path, int(interval), units)

    def save_schedule_to_file(self):
        with open('schedule.txt', 'a') as file:
            for job in self.scheduler.get_jobs():
                file.write(f"{job.id},{job.kwargs['job'][1]},{job.kwargs['job'][2]},{job.kwargs['job'][3]}\n")

    def schedule_task(self, job_id, executable_path, interval, units):
        job_identifier = f"{job_id}_{units}_{interval}"

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Check if the job is already scheduled
        if job_identifier in [job.id for job in self.scheduler.get_jobs()]:
            print(f"Job {job_identifier} already scheduled.{current_time}")
            return

        if units == 'seconds':
            self.scheduler.add_job(
                self.process_task,
                'interval',
                seconds=interval,
                kwargs={'job': (job_id, executable_path, interval, units)}
            )
        elif units == 'minutes':
            self.scheduler.add_job(
                self.process_task,
                'interval',
                minutes=interval,
                kwargs={'job': (job_id, executable_path, interval, units)}
            )
        elif units == 'hours':
            self.scheduler.add_job(
                self.process_task,
                'interval',
                hours=interval,
                kwargs={'job': (job_id, executable_path, interval, units)}
            )
        elif units == 'daily':
            self.scheduler.add_job(
                self.process_task,
                'interval',
                days=interval,
                kwargs={'job': (job_id, executable_path, interval, units)}
            )
        elif units == 'weekly':
            self.scheduler.add_job(
                self.process_task,
                'interval',
                weeks=interval,
                kwargs={'job': (job_id, executable_path, interval, units)}
            )
        elif units == 'monthly':
            self.scheduler.add_job(
                self.process_task,
                'cron',
                month='*',
                day=interval,
                kwargs={'job': (job_id, executable_path, interval, units)}
            )
        elif units == 'yearly':
            self.scheduler.add_job(
                self.process_task,
                'cron',
                month='*',
                day=interval,
                kwargs={'job': (job_id, executable_path, interval, units)}
            )

        # Save the updated schedule to file
        # self.save_schedule_to_file()

def start_scheduler(task_queue, result_queue):
    scheduler_instance = TaskScheduler(task_queue, result_queue)
    scheduler_instance.scheduler.start()
    try:
        loop = asyncio.get_event_loop()
        # loop.create_task(scheduler_instance.process_task(('initial', 'ping microsoft.com -t -4 > D:\wr.txt', 60, 'minutes')))
        loop.create_task(scheduler_instance.process_task(('initial', 'cls && ping microsoft.com -t -4', 60, 'minutes')))
        loop.run_forever()
    finally:
        # Clean up resources
        scheduler_instance.cleanup()

def worker_process(task_queue, result_queue):
    process = multiprocessing.Process(target=start_scheduler, args=(task_queue, result_queue))
    process.start()
    process.join()

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

    scheduler_instance = TaskScheduler(task_pipes[0][0], result_pipes[0][0])

    try:
        while True:
            job_id, executable_path, interval, units = input(
                "Enter Job ID, Executable Path, Interval, and Units (seconds, minutes, hours, daily, weekly, monthly, yearly), or 'exit' to quit: ").split(",")

            if job_id.lower() == 'exit':
                break

            # Distribute tasks among worker processes
            scheduler_instance.schedule_task(int(job_id), executable_path, int(interval), units)

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
