import logging
import json
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Use a dictionary to store pointers
pointers = {}
pointers_pos={}
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
                match = re.match(r"(\d+)(.+)", line)
                if match:
                    index = int(match.group(1))
                    value = match.group(2).strip()

                    # Ensure the list is big enough
                    ensure_size(pointers_names, index)

                    # Place the value at the correct index in the list
                    pointers_names[index] = value

                    logging.debug(f"Index {index}: {value}")

    logging.debug(f"Pointer names for {pointer}: {pointers_names}")
    pointers[pointer] = pointers_names
    return pointers_names

def parse_schema(schema):
    logging.debug(f"Raw schema: {schema}")

    # Replace the curly braces and colons to match the desired JSON format
    formatted_string = schema.replace("{", '{"').replace("}", '"}').replace(":", '": "').replace(",", '", "')

    # Parse the formatted string into a Python object
    parsed_object = json.loads(formatted_string)

    # Print the resulting object
    logging.debug(f"Parsed schema: {parsed_object}")
    return parsed_object

def get_pointer_pos(pointer, name):
    if pointer not in pointers:
        pointers[pointer]={}
    if name in pointers[pointer]:
        return pointers[pointer][name]
    with open(f"pplang/pointers/{pointer}", 'r') as file:
        for line in file:
            # Remove any leading/trailing whitespace characters
            line = line.strip()

            # Ensure the line is not empty
            if line:
                match = re.match(r"(\d+)(.+)", line)
                if match:
                    index = int(match.group(1))
                    value = match.group(2).strip()

                    if value == name:
                        pointers[pointer][name] = index
                        return index
    return None

def process_object(schema, obj):
    logging.debug(f"Processing object with schema: {schema} and object: {obj}")

    if isinstance(schema, list):
        compiled_result = []
        for item in obj:
            compiled_item = [None] * len(schema[0])  # Initialize the compiled_item list with the correct size
            idx = 0
            for key, value in schema[0].items():
                if value in item:
                    pointers_pos[key] = {}
                    item_value = item[value]
                    key_pointer_index = get_pointer_pos(key, item_value)
                    compiled_item[idx] = key_pointer_index
                    idx += 1
            compiled_result.append(compiled_item)

        return compiled_result

def compile(pointer, obj):
    pointers_pos[pointer] = {}

    # Get the pointer names
    pointers_names = get_pointer_names(pointer)

    # The schema is expected at position 0
    raw_schema = pointers_names[0]
    schema = parse_schema(raw_schema)

    compiled_result = process_object(schema, obj)
    return compiled_result

# Example usage
pointer = 'ui_color_palette_schema'  # The pointer file should be located at pplang/pointers/ui_color_palette_schema
obj_array = [
    {'color': 'Alice Blue', 'type': 'Subtle background color'},
    {'color': 'White Smoke', 'type': 'Alert color'}
]

compiled_object_array = compile(pointer, obj_array)
print(compiled_object_array)
