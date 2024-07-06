from implementations.python.operators.memory import allocate_memory_to_operator
from implementations.python.operators.task import task_manager
from implementations.python.operators.magic import magic_wand
from implementations.python.spells.expecto_patronum import expecto_patronum
from implementations.python.apps import PPLangApp

class OSApp:
    def __init__(self):
        self.memory = self._initialize_memory()
        self.task_manager = task_manager
        self.magic_wand = magic_wand
        self.apps = {}

        pplang_app = PPLangApp(self)
        self.register_app("pplang", pplang_app)

    @magic_wand(None, "shake_hand", "handshakes_for_memory_allocation_to_operators")
    def _initialize_memory(self):
        os_memory_space_id = allocate_memory_to_operator()
        # os_tmp_memory = 
        return {
            "os_memory_space_id": os_memory_space_id,
        }

    def register_app(self, app_name, app_instance):
        self.apps[app_name] = app_instance

    def route(self, app_name, function_name, *args, **kwargs):
        if app_name in self.apps:
            app = self.apps[app_name]
            if hasattr(app, function_name):
                func = getattr(app, function_name)
                return func(*args, **kwargs)
        raise Exception(f"Route {app_name}.{function_name} not found")
