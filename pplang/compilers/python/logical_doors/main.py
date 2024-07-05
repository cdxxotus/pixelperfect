
def make_new_uncompilation():
    state = {
        "uncompiled_string": "",
        "live_memory": {}
    }
    
    def get_pointer_name_at_pos(pos):
        # trytogetit from memory
        # else from pointers
        pointer_name=""
        state["live_memory"][pos]=pointer_name

    def make_new_operation():
        return {
            
        }
    
    return {
        "doors": {
            """any""": {
                "uncompilation_state_update": {
                    "is_escaped": False,
                }
            },
            """pointer_pos""": {
                "uncompilation_state_update": {},
                "uncompilation_memory_get": {"pointer_name": get_pointer_name_at_pos},
                "uncompilation_schema_build": {"append": f""},
            },
            """$""": {},
            """+""": {},
            """*""": {},
            """€""": {
                "uncompilation_state_update": {
                    "is_escaped": True,
                }
            },
            """$""": {},
            """@""": {},
            """{""": {
                "uncompilation_state_update": {
                    "schema_object_key_idx": 0,
                }
            },
            """}""": {},
            """[""": {
                "uncompilation_state_update": {
                    "schema_tupple_idx": 0,
                }
            },
            """]""": {},
            """(""": {
                "uncompilation_state_update": {
                    "in_parenthesis": True,
                }
            },
            """)""": {
                "uncompilation_state_update": {
                    "in_parenthesis": False,
                }
            },
            """,""": {},
        },
    }
    
uncompilations=[]
