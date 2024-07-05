import inspect
import uuid

def make(session_state):
    spells_registry = {}
    magic_context = {}
    handshakes_pending = {}
    # hands_in_hands={}

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
                    if behavior=="magic_context":
                        magic_context_number=None
                        if behavior_args[0]:
                            magic_context_number=behavior_args[0]
                            kwargs['magic_context'] = magic_context[behavior_args[0]]
                        else:
                            magic_context_number=uuid.uuid4()
                            kwargs['magic_context'] = magic_context[magic_context_number]
                            kwargs['magic_context_number']=magic_context_number
                        if behavior_args[1]:
                            magic_context[magic_context_number]**=behavior_args[1]
                    if behavior=="handshake_required":
                        handshakes_pending.set(behavior_args[2], behavior_args[1])
                        handshake_secret_dict={} if not kwargs["handshake_secret"] else kwargs["handshake_secret"]
                        if handshake_secret_dict.get(behavior_args[2]) in behavior_args[1].keys():
                            pass
                        else:
                            None
                    if behavior=="shake_hand":
                        # hand_in_hand={"shaker":{
                        #     "args": behavior_args
                        # }, "handler": None}
                        if handshakes_pending[behavior_args[0]]:
                            if handshakes_pending[behavior_args[0]][behavior_args[1]]:
                                handshakd_secret_dict={} if not kwargs["handshake_secret"] else kwargs["handshake_secret"]
                                handshakd_secret_dict.set(behavior_args[0], handshakes_pending[behavior_args[0]][behavior_args[1]])
                                # hand_in_hand["shaker"]["verified_handshake_value"]=handshakes_pending[behavior_args[0]][behavior_args[1]]
                                # hands_in_hands[handshakes_pending[behavior_args[0]][behavior_args[1]]] = hand_in_hand
                                kwargs["handshake_secret"] = handshakd_secret_dict
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
                        apply_spell(behavior)
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
