import logging
import json
import re
import time

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

# Use a dictionary to store pointers
pointers_names = {}
unicode_map = []
reserved_chars = set()

# Load the reserved characters from the reserved file
with open("pplang/hard/reserved", 'r') as file:
    for line in file:
        line = line.strip()
        reserved_chars.update(list(line))
        
# Load the Unicode characters from the reserved/unicodes file
with open("pplang/hard/unicodes", 'r') as file:
    for line in file:
        line = line.strip()
        unicode_map.extend(list(line))

# Function to ensure the list is big enough to hold the value at the given index
def ensure_size(lst, index):
    while len(lst) <= index:
        lst.append(None)

# Read the file and parse each line
def get_pointer_names(pointer):
    self_pointers_names = []
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
                    ensure_size(self_pointers_names, index)

                    # Place the value at the correct index in the list
                    self_pointers_names[index] = value

                    logging.debug(f"Index {index}: {value}")

    logging.debug(f"Pointer names for {pointer}: {pointers_names}")
    pointers_names[pointer] = self_pointers_names
    return self_pointers_names

def parse_schema(schema):
    logging.debug(f"Raw schema: {schema}")

    # Replace the curly braces and colons to match the desired JSON format
    formatted_string = schema.replace("{", '{"').replace("}", '"}').replace(":", '": "').replace(",", '", "')

    # Parse the formatted string into a Python object
    parsed_object = json.loads(formatted_string)

    # Print the resulting object
    logging.debug(f"Parsed schema: {parsed_object}")
    return parsed_object

def get_pointer_pos(pointers_pos, pointer, name):
    if pointer not in pointers_pos:
        pointers_pos[pointer] = {}
    if name in pointers_pos[pointer]:
        return pointers_pos[pointer][name]
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
                        pointers_pos[pointer][name] = index
                        return index
    return None

def process_object(schema, obj):
    logging.debug(f"Processing object with schema: {schema} and object: {obj}")
    self_pointers_pos = {}
    if isinstance(schema, list):
        compiled_result = []
        for item in obj:
            compiled_item = [None] * len(schema[0])  # Initialize the compiled_item list with the correct size
            idx = 0
            for key, value in schema[0].items():
                if value in item:
                    if idx == 0:
                        self_pointers_pos[key] = {}
                    item_value = item[value]
                    key_pointer_index = get_pointer_pos(self_pointers_pos, key, item_value,)
                    compiled_item[idx] = key_pointer_index
                    idx += 1
            compiled_result.append(compiled_item)

        return compiled_result

def compile(pointer, obj):
    start_time = time.time()  # Start time

    # Get the pointer names
    schema_pointers_names = get_pointer_names(pointer)
    shema_pointer_pos = get_pointer_pos({}, "=", pointer)

    # The schema is expected at position 0
    raw_schema = schema_pointers_names[0]
    schema = parse_schema(raw_schema)

    compiled_result = f"${shema_pointer_pos}{process_object(schema, obj)}".replace(" ", "").replace("None", "-").replace("],[", '|').replace("[[", "[").replace("]]", "]")
    
    # Convert numbers to corresponding Unicode characters and escape reserved characters
    unicode_result = ''.join(f"\\{unicode_map[int(num)]}" if num.isdigit() and unicode_map[int(num)] in reserved_chars else unicode_map[int(num)] if num.isdigit() else num for num in re.findall(r'\d+|.', compiled_result))

    end_time = time.time()  # End time
    compilation_time = end_time - start_time
    logging.warning(f"Compilation time: {compilation_time:.6f} seconds")  # Display time with microsecond precision

    return unicode_result

# Example usage
pointer = 'ui_color_palette_schema'  # The pointer file should be located at pplang/pointers/ui_color_palette_schema
data = [
    {
        "color": "Beige",
        "type": "Secondary color",
        "score": 0.9999566078186035
    },
    {
        "color": "Cyan",
        "type": "Notification highlight color",
        "score": 0.9999328851699829
    },
    {
        "color": "Pink",
        "type": "Accent color",
        "score": 0.9999185800552368
    },
    {
        "color": "AliceBlue",
        "type": "Text color",
        "score": 0.999894380569458
    },
    {
        "color": "WhiteSmoke",
        "type": "Border color",
        "score": 0.9998866319656372
    },
    {
        "color": "Purple",
        "type": "Highlight color",
        "score": 0.9998842477798462
    },
    {
        "color": "Azure",
        "type": "Main color",
        "score": 0.9998782873153687
    },
    {
        "color": "AntiqueWhite",
        "type": "Alert color",
        "score": 0.9998581409454346
    },
    {
        "color": "DarkGray",
        "type": "Subtle background color",
        "score": 0.9996941089630127
    }
]


compiled_object_array = compile(pointer, data)
print(compiled_object_array)
