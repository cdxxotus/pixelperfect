def make(session_state):
    def stdout(message, verbosity=None):
        if verbosity is None:
            verbosity = session_state["stdout_verbosity_name"]
        print(f"{verbosity} {''.join(message)}")

    def debug(message):
        if session_state["verbosity"] < 0 or session_state["is_verbose"]:
            stdout(message, "DEBUG")

    def verbose(message):
        stdout(message)

    def silent():
        pass

    def info(message):
        if session_state["verbosity"] > 0 or session_state["is_verbose"]:
            stdout(message, "INFO")

    def important(message):
        if session_state["verbosity"] > 1 or session_state["is_verbose"]:
            stdout(message, "IMPORTANT")

    def warning(message):
        if session_state["verbosity"] > 2 or session_state["is_verbose"]:
            stdout(message, "WARNING")

    def critical(message):
        if session_state["verbosity"] > 3 or session_state["is_verbose"]:
            stdout(message, "CRITICAL")

    def unknown(message, message_verbosity_magic_number=1):
        if session_state["verbosity"] >= message_verbosity_magic_number or session_state["is_verbose"]:
            stdout(message, "UNKNOWN")

    def private(message):
        if session_state["is_dev_mode"]:
            stdout(message, "PRIVATE")

    def system(message):
        if session_state["is_system"]:
            stdout(message, "SYSTEM")

    def developers(message):
        if session_state["is_dev_mode"]:
            stdout(message, "@DEV")

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

def debug():
    return logger["debug"]

def info():
    return logger["info"]

def important():
    return logger["important"]

def warning():
    return logger["warning"]

def critical():
    return logger["critical"]

def unknown():
    return logger["unkonwn"]

def developers():
    return logger["developers"]
