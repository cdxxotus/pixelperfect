import uuid
from collections import deque
from threading import Thread, Lock
from time import sleep
from compilers.python.operators import magic, memory

def make(session_state):
    job_queue = deque()
    workers = []
    job_status = {}
    job_lock = Lock()
    worker_lock = Lock()

    @magic(None, "handshake_required", magic.magic_context.memory_handshake, magic.magic_context)
    def memory_manager():
        operator_memory_id=memory.allocate_memory_to_operator()
        return

    class Job:
        def __init__(self, job_id, data):
            self.job_id = job_id
            self.data = data
            self.status = 'created'
            self.result = None

    class Worker(Thread):
        def __init__(self, worker_id, task_manager):
            super().__init__()
            self.worker_id = worker_id
            self.task_manager = task_manager
            self.busy = False

        def run(self):
            while True:
                job = self.task_manager.get_next_job()
                if job:
                    self.busy = True
                    job.status = 'in_progress'
                    try:
                        # Simulate job processing
                        sleep(2)
                        job.result = f"Processed by worker {self.worker_id}"
                        job.status = 'completed'
                    except Exception as e:
                        job.status = 'failed'
                        job.result = str(e)
                    finally:
                        self.busy = False

    def initialize_workers(num_workers):
        with worker_lock:
            for i in range(num_workers):
                worker = Worker(worker_id=i, task_manager=task_manager)
                workers.append(worker)
                worker.start()

    def add_job(data):
        job_id = str(uuid.uuid4())
        job = Job(job_id, data)
        with job_lock:
            job_queue.append(job)
            job_status[job_id] = job
        return job_id

    def get_next_job():
        with job_lock:
            if job_queue:
                return job_queue.popleft()
        return None

    def get_job_status(job_id):
        with job_lock:
            return job_status.get(job_id)

    task_manager = {
        "add_job": add_job,
        "get_next_job": get_next_job,
        "get_job_status": get_job_status
    }

    if session_state["workers_count_expected"]:
        initialize_workers(session_state["workers_count_expected"])
    # elif: # get it from memory
    # elif: # request OS constant
    else:
        initialize_workers(42)

    return task_manager

# Define the session state
session_state = {
    "verbosity": 2,
    "is_verbose": True,
    "is_dev_mode": True,
    "is_system": False,
    "stdout_verbosity_name": "IMPORTANT",
    "magic": "420",
    "workers_count_expected": 0
}

# Initialize the task manager
task_manager = make(session_state)

def add_job(*args, **kwargs):
    return task_manager["add_job"](*args, **kwargs)

def get_job_status(*args, **kwargs):
    return task_manager["get_job_status"](*args, **kwargs)

# Example usage
# --------------------------------------------------------------------------------------
# if __name__ == "__main__":
#     # Initialize 3 workers
#     task_manager 

#     # Add some jobs
#     job_ids = []
#     for i in range(5):
#         job_id = task_manager["add_job"](f"Job data {i}")
#         job_ids.append(job_id)

#     # Monitor job statuses
#     for job_id in job_ids:
#         status = task_manager["get_job_status"](job_id)
#         print(f"Job ID: {job_id}, Status: {status.status}, Result: {status.result}")

#     # Keep monitoring until all jobs are done
#     while any(task_manager["get_job_status"](job_id).status != 'completed' for job_id in job_ids):
#         for job_id in job_ids:
#             status = task_manager["get_job_status"](job_id)
#             print(f"Job ID: {job_id}, Status: {status.status}, Result: {status.result}")
        # sleep(1)
