class Logger:
    def __init__(self, session_state):
        self.session_state = session_state

    def stdout(self, message, verbosity=None):
        if verbosity is None:
            verbosity = self.session_state["stdout_verbosity_name"]
        print(f"{verbosity} {''.join(message)}")

    def debug(self, message):
        if self.session_state["verbosity"] < 0 or self.session_state["is_verbose"]:
            self.stdout(message, "DEBUG")

    def verbose(self, message):
        self.stdout(message)

    def silent(self):
        pass

    def info(self, message):
        if self.session_state["verbosity"] > 0 or self.session_state["is_verbose"]:
            self.stdout(message, "INFO")

    def important(self, message):
        if self.session_state["verbosity"] > 1 or self.session_state["is_verbose"]:
            self.stdout(message, "IMPORTANT")

    def warning(self, message):
        if self.session_state["verbosity"] > 2 or self.session_state["is_verbose"]:
            self.stdout(message, "WARNING")

    def critical(self, message):
        if self.session_state["verbosity"] > 3 or self.session_state["is_verbose"]:
            self.stdout(message, "CRITICAL")

    def unknown(self, message, message_verbosity_magic_number=1):
        if self.session_state["verbosity"] >= message_verbosity_magic_number or self.session_state["is_verbose"]:
            self.stdout(message, "UNKNOWN")

    def private(self, message):
        if self.session_state["is_dev_mode"]:
            self.stdout(message, "PRIVATE")

    def system(self, message):
        if self.session_state["is_system"]:
            self.stdout(message, "SYSTEM")

    def developers(self, message):
        if self.session_state["is_dev_mode"]:
            self.stdout(message, "@DEV")

# Define the session state
session_state = {
    "verbosity": 2,
    "is_verbose": True,
    "is_dev_mode": True,
    "is_system": False,
    "stdout_verbosity_name": "IMPORTANT"  # Added this key for reference
}

# Instantiate the logger
logger = Logger(session_state)

# Example developer message at instantiation
logger.developers("Thank you for being here, I hope you appreciate this message created just for you.")

# Example usage
# ----------------------------------------------------------------
# logger.debug("This is a debug message")
# logger.verbose("This is a verbose message")
# logger.info("This is an info message")
# logger.important("This is an important message")
# logger.warning("This is a warning message")
# logger.critical("This is a critical message")
# logger.unknown("This is an unknown verbosity message", 2)
# logger.private("This is a private message")
# logger.system("This is a system message")
# logger.developers("This is a developer message")
