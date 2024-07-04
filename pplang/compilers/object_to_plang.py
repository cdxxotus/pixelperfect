import re

# Function to ensure the list is big enough to hold the value at the given index
def ensure_size(lst, index):
    while len(lst) <= index:
        lst.append(None)

# Read the file and parse each line
def get_pointer_names(pointer):
    pointers_names = []
    with open(f"pplang/pointers/{pointer}", 'r') as file:
        for line in file:
            # Remove any leading/trailing whitespace characters
            line = line.strip()

            # Ensure the line is not empty
            if line:
                # Extract the index from the first character
                index = int(line[0])
                # Extract the value from the rest of the line
                value = line[1:]

                # Ensure the list is big enough
                ensure_size(pointers_names, index)

                # Place the value at the correct index in the list
                pointers_names[index] = value

    return pointers_names

def parse_schema(schema):
    # Remove whitespace
    schema = schema.replace(" ", "")

    # Check if the schema is an array or an object
    if schema.startswith("[") and schema.endswith("]"):
        is_array = True
        # Remove the surrounding brackets
        schema = schema[1:-1]
    elif schema.startswith("{") and schema.endswith("}"):
        is_array = False
        # Remove the surrounding braces
        schema = schema[1:-1]
    else:
        raise ValueError("Invalid schema format")

    # Extract the keys
    pattern = r'{([^:]+):([^,}]+)}'
    matches = re.findall(pattern, schema)

    if is_array:
        result = [{key: None} for key, _ in matches]
    else:
        result = {key: None for key, _ in matches}

    return result

def compile(pointer, obj):
    # Get the pointer names
    pointers_names = get_pointer_names(pointer)

    # The schema is expected at position 0
    raw_schema = pointers_names[0]
    schema = parse_schema(raw_schema)

    def find_pointer_index(pointers_names, key):
        try:
            return pointers_names.index(key)
        except ValueError:
            return None

    def process_object(schema, obj):
        if isinstance(schema, list):
            compiled_result = []
            for item in obj:
                compiled_item = {}
                for entry in schema:
                    for key in entry.keys():
                        if key in item:
                            value = item[key]
                            key_pointer_index = find_pointer_index(pointers_names, key)
                            value_pointer_index = find_pointer_index(pointers_names, value)
                            if key_pointer_index is not None and value_pointer_index is not None:
                                compiled_item[key_pointer_index] = value_pointer_index
                compiled_result.append(compiled_item)
        else:
            compiled_result = {}
            for key in schema.keys():
                if key in obj:
                    value = obj[key]
                    key_pointer_index = find_pointer_index(pointers_names, key)
                    value_pointer_index = find_pointer_index(pointers_names, value)
                    if key_pointer_index is not None and value_pointer_index is not None:
                        compiled_result[key_pointer_index] = value_pointer_index

        return compiled_result

    return process_object(schema, obj)

# Example usage
pointer = 'ui_color_palette_schema'  # The pointer file should be located at pplang/pointers/ui_color_palette_schema
obj_array = [
    {'color': 'Alice Blue', 'type': 'Subtle background color'},
    {'color': 'White Smoke', 'type': 'Alert color'}
]

compiled_object_array = compile(pointer, obj_array)
print(compiled_object_array)
