from implementations.python.operators.memory import allocate_memory_to_operator
from implementations.python.operators.magic import magic_wand

class PPLangApp:
    def __init__(self, os_instance):
        self.os = os_instance
        self.memory = self._initialize_memory()

    @magic_wand(None, "shake_hand", "handshakes_for_memory_allocation_to_operators")
    def _initialize_memory(self):
        os_memory_space_id = allocate_memory_to_operator()
        # os_tmp_memory = 
        return {
            "os_memory_space_id": os_memory_space_id,
        }
    
    def add_task(self, data):
        return self.os.task_manager["add_job"](data)

    def get_task_status(self, job_id):
        return self.os.task_manager["get_job_status"](job_id)
