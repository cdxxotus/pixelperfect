import inspect

def make(session_state):
    spells_registry = {}

    def register_spell(name, func):
        spells_registry[name] = func

    def apply_spell(spell_name):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if spell_name in spells_registry:
                    return spells_registry[spell_name](func, *args, **kwargs)
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def magify(magic_number=None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if session_state["magic_number"] != 420 and magic_number != 420:
                    return None
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def magic_wand(magic_number=None, behavior=None, behavior_args=[], behavior_context={}):
        def wand(func):
            def wrapped_func(*args, **kwargs):
                if magic_number != 420:
                    if behavior == "log":
                        pass
                    elif behavior == "modify_args":
                        args = tuple("42" if isinstance(arg, str) else arg for arg in args)
                    elif behavior == "default_return":
                        return 42
                    elif behavior == "reserved":
                        stack = inspect.stack()
                        caller_parent_frame = stack[2] if len(stack) > 2 else None
                        func_parent_frame = stack[3] if len(stack) > 3 else None
                        
                        if caller_parent_frame and func_parent_frame and caller_parent_frame.function == func_parent_frame.function and inspect.stack()[1].function in behavior_args:
                            pass
                        else:
                            return 42
                    elif behavior=="learn_spell":
                        register_spell(behavior_args[0],behavior_args[1])
                        pass
                    elif behavior in spells_registry.keys():
                        apply_spell(behavior_args)
                        pass
                    return None
                return func(*args, **kwargs)
            return wrapped_func
        return wand

    return {
        "magify": magify,
        "magic_wand": magic_wand,
    }

# Define the session state
session_state = {
    "verbosity": 2,
    "is_verbose": True,
    "is_dev_mode": True,
    "is_system": False,
    "stdout_verbosity_name": "IMPORTANT",
    "magic": 420
}

# Get the magic functions
magic = make(session_state)

# Wrapper functions
def magify(*args, **kwargs):
    return magic["magify"](*args, **kwargs)

def magic_wand(*args, **kwargs):
    return magic["magic_wand"](*args, **kwargs)

# Example usage
# -------------------------------------------------------------------
