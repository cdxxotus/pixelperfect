def make(session_state):
    def debug(message):
        if session_state["verbosity"] < 0 or session_state["is_verbose"]:
            _stdout(message, "DEBUG")

    def verbose(message):
        _stdout(message)

    def silent():
        pass

    def info(message):
        if session_state["verbosity"] > 0 or session_state["is_verbose"]:
            _stdout(message, "INFO")

    def important(message):
        if session_state["verbosity"] > 1 or session_state["is_verbose"]:
            _stdout(message, "IMPORTANT")

    def warning(message):
        if session_state["verbosity"] > 2 or session_state["is_verbose"]:
            _stdout(message, "WARNING")

    def critical(message):
        if session_state["verbosity"] > 3 or session_state["is_verbose"]:
            _stdout(message, "CRITICAL")

    def unknown(message, message_verbosity_magic_number=1):
        if session_state["verbosity"] >= message_verbosity_magic_number or session_state["is_verbose"]:
            _stdout(message, "UNKNOWN")

    def private(message):
        if session_state["is_dev_mode"]:
            _stdout(message, "PRIVATE")

    def system(message):
        if session_state["is_system"]:
            _stdout(message, "SYSTEM")

    def developers(message):
        if session_state["is_dev_mode"]:
            _stdout(message, "@DEV")

    def _stdout(message, verbosity=None):
        if verbosity is None:
            verbosity = session_state["stdout_verbosity_name"]
        print(f"{verbosity} {''.join(message)}")

    # Return a dictionary of functions
    return {
        "debug": debug,
        "verbose": verbose,
        "silent": silent,
        "info": info,
        "important": important,
        "warning": warning,
        "critical": critical,
        "unknown": unknown,
        "private": private,
        "system": system,
        "developers": developers
    }

# Define the session state
session_state = {
    "verbosity": 2,
    "is_verbose": True,
    "is_dev_mode": True,
    "is_system": False,
    "stdout_verbosity_name": "IMPORTANT"  # Added this key for reference
}

# Get the logger functions
logger = make(session_state)
logger["developers"]("thank you for being here, i hope you appreciate this message created just for you")

# Example usage
# --------------------------------------------------------
# logger["debug"]("This is a debug message")
# logger["verbose"]("This is a verbose message")
# logger["info"]("This is an info message")
# logger["important"]("This is an important message")
# logger["warning"]("This is a warning message")
# logger["critical"]("This is a critical message")
# logger["unknown"]("This is an unknown verbosity message", 2)
# logger["private"]("This is a private message")
# logger["system"]("This is a system message")
# logger["developers"]("This is a developer message")

def debug(*args, **kwargs):
    return logger["debug"](*args, **kwargs)

def info(*args, **kwargs):
    return logger["info"](*args, **kwargs)

def important(*args, **kwargs):
    return logger["important"](*args, **kwargs)

def warning(*args, **kwargs):
    return logger["warning"](*args, **kwargs)

def critical(*args, **kwargs):
    return logger["critical"](*args, **kwargs)

def unknown(*args, **kwargs):
    return logger["unknown"](*args, **kwargs)

def developers(*args, **kwargs):
    return logger["developers"](*args, **kwargs)
