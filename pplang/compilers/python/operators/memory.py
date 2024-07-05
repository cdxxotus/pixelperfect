import uuid

def make():
    temp_memory_spaces = {}
    app_memory_spaces = {}

    context={
        "^": {
            temp_memory_spaces: {},
            app_memory_spaces: {}
        },
        "œ": {
            temp_memory_spaces: {},
            app_memory_spaces: {}
        }
    }

    # Create a unique identifier for the temporary memory space
    def _create_temp_memory_space(context=context["œ"]):
        unique_id = str(uuid.uuid4())
        if context:
            context.temp_memory_spaces[unique_id] = {}
        else:
            temp_memory_spaces[unique_id] = {}
        return unique_id

    # Create a unique identifier for the application-wide memory space
    def _create_app_memory_space(context=context["œ"]):
        unique_id = str(uuid.uuid4())
        if context:
            context.app_memory_spaces[unique_id] = {}
        else:
            app_memory_spaces[unique_id] = {}
        return unique_id
 
    def make_for_admins(self, context=context["œ"]):
        temp_memory_spaces = context.temp_memory_spaces
        app_memory_spaces = context.app_memory_spaces

        def create_temp_memory_space():
            return _create_temp_memory_space(context)
        
        def create_app_memory_space():
            return _create_app_memory_space(context)

        # Retrieve the temporary memory space using the unique identifier
        def get_temp_memory_space(self, space_id):
            return temp_memory_spaces.get(space_id)

        # Retrieve the application-wide memory space using the unique identifier
        def get_app_memory_space(self, space_id):
            return app_memory_spaces.get(space_id)

        # Allocate memory in a temporary memory space
        def allocate_temp_memory(self, space_id, key, value):
            if space_id in temp_memory_spaces:
                temp_memory_spaces[space_id][key] = value

        # Allocate memory in an application-wide memory space
        def allocate_app_memory(self, space_id, key, value):
            if space_id in app_memory_spaces:
                app_memory_spaces[space_id][key] = value

        # Deallocate memory in a temporary memory space
        def deallocate_temp_memory(self, space_id, key):
            if space_id in temp_memory_spaces and key in temp_memory_spaces[space_id]:
                del temp_memory_spaces[space_id][key]

        # Deallocate memory in an application-wide memory space
        def deallocate_app_memory(self, space_id, key):
            if space_id in app_memory_spaces and key in app_memory_spaces[space_id]:
                del app_memory_spaces[space_id][key]

        # Clear all temporary memory spaces
        def clear_temp_memory(self):
            temp_memory_spaces.clear()

        # Clear all application-wide memory spaces
        def clear_app_memory(self):
            app_memory_spaces.clear()

        return {
            "clear_temp_memory": clear_temp_memory,
            "clear_app_memory": clear_app_memory,
            "deallocate_app_memory": deallocate_app_memory,
            "deallocate_temp_memory": deallocate_temp_memory,
            "allocate_app_memory": allocate_app_memory,
            "allocate_temp_memory": allocate_temp_memory,
            "get_app_memory_space": get_app_memory_space,
            "get_temp_memory_space": get_temp_memory_space,
            "create_temp_memory_space": create_temp_memory_space,
            "create_app_memory_space": create_app_memory_space
        }
    
    app_id=_create_app_memory_space(None)
    temp_memory_space_id=_create_temp_memory_space(None)

    memory = make_for_admins("^")
    session_memory = make_for_admins()

    return {
        "make_for_admins": make_for_admins,
        **session_memory
    }

# Define the session state
session_state = {
    "verbosity": 2,
    "is_verbose": True,
    "is_dev_mode": True,
    "is_system": False,
    "stdout_verbosity_name": "IMPORTANT",
    "magic": "420"
}

memory=make(session_state)
memory_for_admins=memory["make_for_admins"]()

# Wrapper functions
def create_app_memory_space(*args, **kwargs):
    return memory_for_admins["create_app_memory_space"](*args, **kwargs)

def create_temp_memory_space(*args, **kwargs):
    return memory_for_admins["create_temp_memory_space"](*args, **kwargs)

# Example usage
# ------------------------------------------------------------------

