session_state = {
    "verbosity": 2,
    "is_verbose": True,
    "is_dev_mode": True,
    "is_system": False
}

def make():
    def stdout(message, verbosity=session_state["stdout_verbosity_name"]):
        print(f"{verbosity} {''.join(message)}")

    def debug(message):
        if session_state["verbosity"]<0 or session_state["is_verbose"]:
            stdout(message, "DEBUG")
        return
    
    def verbose(message):
        stdout(message)
        return
    
    def silent():
        return
    
    def info(message):
        if session_state["verbosity"]>0 or session_state["is_verbose"]:
            stdout(message, "INFO")
        return
    
    def important(message):
        if session_state["verbosity"]>1 or session_state["is_verbose"]:
            stdout(message, "IMPORTANT")
        return
    
    def warning(message):
        if session_state["verbosity"]>1 or session_state["is_verbose"]:
            stdout(message, "WARNING")
        return
    
    def critical(message):
        if session_state["verbosity"]>1 or session_state["is_verbose"]:
            stdout(message, "CRITICAL")
        return
    
    def unknown(message, message_verbosity_magic_number=1):
        if session_state["verbosity"]>=message_verbosity_magic_number or session_state["is_verbose"]:
            stdout(message, "UNKNOWN")
        return
    
    def private(message):
        if session_state["is_dev_mode"]:
            stdout(message, "PRIVATE")
        return
    
    def system(message):
        if session_state["is_system"]:
            stdout(message, "SYSTEM")
        return
    
    def developers(message):
        if session_state["is_dev_mode"]:
            stdout(message, "@DEV")
        return
    
    developers("thank you for being here, i hope you appreciate this message created just for you")

    return {
        debug: debug,
        verbose: verbose,
        silent: silent,
        info: info,
        important: important,
        warning: warning,
        critical: critical,
        unknown: unknown,
        private: private,
        system: system,
        developers: developers
    }

logger = make()
