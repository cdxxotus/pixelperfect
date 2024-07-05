def make_new_uncompilation(start_at_pos, start_at_char, string_to_uncompile):
    state = {
        "uncompiled_string": "",
        "live_memory": {},
        "uncompiled_chars": 0,
        "operation": None
    }

    def string_yielder(string_to_yield):
        current_char = None

        def pass_to_next_char_and_get_next_char():
            nonlocal current_char
            for char in string_to_yield:
                current_char = char
                yield char

        def jump_to_next_logical_door_and_get_substring():
            substring = current_char
            for char in pass_to_next_char_and_get_next_char():
                current_char = char
                # if char == "$": # beware of escaped $
                #     return substring
                # substring += char
            return substring

        return {
            "pass_to_next_char_and_get_next_char": pass_to_next_char_and_get_next_char,
            "jump_to_next_logical_door_and_get_substring": jump_to_next_logical_door_and_get_substring
        }

    def get_pointer_name_at_pos(pos):
        # try to get it from memory
        # else from pointers
        pointer_name = ""
        state["live_memory"][pos] = pointer_name

    def make_new_operation(operation_string):
        operation_yielder = string_yielder(operation_string)

        def passe():
            char = next(operation_yielder["pass_to_next_char_and_get_next_char"]())

        return {
            "passe": passe
        }

    def passe():
        if state.operation:
            state.operation.passe()
        else:
            make_new_operation()
            state.operation.passe()
        return

    doors = {
        "any": {
            "uncompilation_state_update": {
                "is_escaped": False,
            }
        },
        "pointer_pos": {
            "uncompilation_state_update": {},
            "uncompilation_memory_get": {"pointer_name": get_pointer_name_at_pos},
            "uncompilation_schema_build": {"append": f""},
        },
        "$": {},
        "+": {},
        "*": {},
        "€": {
            "uncompilation_state_update": {
                "is_escaped": True,
            }
        },
        "@": {},
        "{": {
            "uncompilation_state_update": {
                "schema_object_key_idx": 0,
            }
        },
        "}": {},
        "[": {
            "uncompilation_state_update": {
                "schema_tuple_idx": 0,
            }
        },
        "]": {},
        "(": {
            "uncompilation_state_update": {
                "in_parenthesis": True,
            }
        },
        ")": {
            "uncompilation_state_update": {
                "in_parenthesis": False,
            }
        },
        ",": {},
    }

    def progress():
        return state["uncompiled_chars"] / len(string_to_uncompile)


    def uncompilation_yielder():
        while True:
            yield {
                "passe": passe,
                "progress": progress
            }

    return uncompilation_yielder
