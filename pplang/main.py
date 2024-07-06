from implementations.python.apps import OSApp
from implementations.python.operators import memory

def make():
    state={
        "memory": None,
        "os_instance": None,
        "session_state":{
            "verbosity": 2,
            "is_verbose": True,
            "is_dev_mode": True,
            "is_system": False,
            "stdout_verbosity_name": "IMPORTANT",
            "magic": "420"
        }
    }

    def _initialize_memory():
        state.set("memory", memory.make(state.get("session_state")))
        memory_for_admins=state["memory"]["make_for_admins"]()

        # Wrapper functions
        def create_app_memory_space(*args, **kwargs):
            return memory_for_admins["create_app_memory_space"](*args, **kwargs)

        def create_temp_memory_space(*args, **kwargs):
            return memory_for_admins["create_temp_memory_space"](*args, **kwargs)

        def allocate_memory_to_operator(*args, **kwargs):
            return memory["allocate_memory_to_operator"](*args, **kwargs)

        return {
            "create_app_memory_space": create_app_memory_space
        }

    def _boot_os():
        state.set("os_instance", OSApp())
        pass

    def expose_functions(os_instance):
        def create_app():
            return os_instance.route("pplang", "create_app")

        return {
            "create_app": create_app,
        }

    _initialize_memory()
    _boot_os()
    
    exposed_functions = expose_functions(state.get("os_instance"))

    print("OS Booted and pplang App Initialized")

    return {
        "exposed_functions": exposed_functions
    }

pplang = make()

def create_app(*args, **kwargs):
    return pplang["create_app"](*args, **kwargs)
