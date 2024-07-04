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
unicode_to_index = {}

def load_reserved_chars(filename):
    with open(filename, 'r') as file:
        for line in file:
            reserved_chars.update(line.strip())

def load_unicode_map(filename):
    with open(filename, 'r') as file:
        unicode_map.extend(file.read().strip())
        for idx, char in enumerate(unicode_map):
            unicode_to_index[char] = idx

load_reserved_chars("pplang/hard/reserved")
load_unicode_map("pplang/hard/unicodes")

def ensure_size(lst, index):
    if len(lst) <= index:
        lst.extend([None] * (index + 1 - len(lst)))

def get_pointer_names(pointer):
    if pointer in pointers_names:
        return pointers_names[pointer]
    
    self_pointers_names = []
    try:
        with open(f"pplang/pointers/{pointer}", 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    match = re.match(r"(\d+)(.+)", line)
                    if match:
                        index = int(match.group(1))
                        value = match.group(2).strip()
                        ensure_size(self_pointers_names, index)
                        self_pointers_names[index] = value
    except FileNotFoundError:
        logging.error(f"Pointer file not found: {pointer}")
    
    pointers_names[pointer] = self_pointers_names
    return self_pointers_names

def parse_schema(schema):
    try:
        formatted_string = schema.replace("{", '{"').replace("}", '"}').replace(":", '": "').replace(",", '", "')
        return json.loads(formatted_string)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse schema: {e}")
        return {}

def get_pointer_pos(pointers_pos, pointer, name):
    if pointer not in pointers_pos:
        pointers_pos[pointer] = {}
    
    if name in pointers_pos[pointer]:
        return pointers_pos[pointer][name]
    
    try:
        with open(f"pplang/pointers/{pointer}", 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    match = re.match(r"(\d+)(.+)", line)
                    if match:
                        index = int(match.group(1))
                        value = match.group(2).strip()
                        if value == name:
                            pointers_pos[pointer][name] = index
                            return index
    except FileNotFoundError:
        logging.error(f"Pointer file not found: {pointer}")
    
    return None

def process_object(schema, obj):
    self_pointers_pos = {}
    compiled_result = []

    if isinstance(schema, list):
        for item in obj:
            compiled_item = [None] * len(schema[0])
            idx = 0
            for key, value in schema[0].items():
                if value in item:
                    if idx == 0:
                        self_pointers_pos[key] = {}
                    item_value = item[value]
                    key_pointer_index = get_pointer_pos(self_pointers_pos, key, item_value)
                    compiled_item[idx] = key_pointer_index
                    idx += 1
            compiled_result.append(compiled_item)
    
    return compiled_result

def compile(pointer, obj):
    start_time = time.time()

    schema_pointers_names = get_pointer_names(pointer)
    schema_pointer_pos = get_pointer_pos({}, "=", pointer)

    raw_schema = schema_pointers_names[0] if schema_pointers_names else ""
    schema = parse_schema(raw_schema)

    processed_obj = process_object(schema, obj)
    compiled_result = f"${schema_pointer_pos}{processed_obj}".replace(" ", "").replace("None", "-").replace("],[", '|').replace("[[", "[").replace("]]", "]")
    
    unicode_result = ''.join(f"\\{unicode_map[int(num)]}" if num.isdigit() and unicode_map[int(num)] in reserved_chars else unicode_map[int(num)] if num.isdigit() else num for num in re.findall(r'\d+|.', compiled_result))

    end_time = time.time()
    logging.warning(f"Compilation time: {end_time - start_time:.6f} seconds")

    return unicode_result

def next_char(compiled_str):
    for char in compiled_str:
        yield char

def uncompile(compiled_str):
    start_time = time.time()

    # Initialize state variables
    char_gen = next_char(compiled_str)
    decoded_data = ""
    is_escaped = False
    schema=[]
    current_operation=""
    previous_operation=""
    x_schema = 0
    x_array=0
    x_object=0

    for char in char_gen:
        if char == '\\' and is_escaped == False:
            # Set escape flag
            is_escaped = True
        elif char == '$' and is_escaped == False:
            previous_operation=current_operation
            current_operation="$"
        elif char=="[" and is_escaped==False:
            x_array = 0;
            x_object=0
            decoded_data = f"{decoded_data}{char}"
            previous_operation=current_operation
            current_operation="[{"
        elif (char == ',') and is_escaped==False:
            decoded_data = f"{decoded_data}{char}"
        elif char == ']' and is_escaped==False:
            if current_operation=="{":
                decoded_data = f"{decoded_data}{'}'}{char}"
            else:
                decoded_data = f"{decoded_data}{char}"
            x_object = 0
            x_array=0
        elif char == '|' and is_escaped==False:
            if current_operation=="{":
                decoded_data = f"{decoded_data}{'}'},{'{'}"
            else:
                decoded_data = f"{decoded_data}],["
            x_object=0
            previous_operation=current_operation
            current_operation = "{"
        else:
            # Convert Unicode character to its index
            is_escaped=False
            pos =int(unicode_to_index[char])

            if current_operation=="$":
                schema_list_pointers_names = get_pointer_names("=")
                schema_name=schema_list_pointers_names[pos]
                raw_schema=get_pointer_names(schema_name)[0]
                schema = parse_schema(raw_schema)
                previous_operation=current_operation
                current_operation=""
            elif len(current_operation) == 2 and f"{current_operation[0]}{current_operation[1]}" == "[{":
                key=list(schema[0].keys())[x_object]
                pointer_name=get_pointer_names(key)[pos]
                decoded_data = f"{decoded_data}{'{'}\"{schema[0][key]}\":\"{pointer_name}\""
                x_object=1
                previous_operation=current_operation
                current_operation = "{"
            elif len(current_operation) == 1 and f"{current_operation[0]}" == "{":
                keys=list(schema[0].keys())
                key=list(schema[0].keys())[x_object]
                pointer_name=get_pointer_names(key)[pos]
                decoded_data = f"{decoded_data}\"{schema[0][key]}\":\"{pointer_name}\""
                x_object=x_object+1



    decoded_data = ''.join(decoded_data)

    # Replace symbols with appropriate delimiters
    decoded_data = decoded_data.replace('|', '],[').replace('[', '[[').replace(']', ']]').replace('-', 'None')

    # Convert string back to list
    try:
        compiled_list = json.loads(decoded_data)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse decoded data: {e}")
        return None

    end_time = time.time()
    logging.warning(f"Uncompilation time: {end_time - start_time:.6f} seconds")

    return compiled_list

# Example usage
pointer = 'ui_color_palette_schema'
data = [
    {"color": "Beige", "type": "Secondary color", "score": 0.9999566078186035},
    {"color": "Cyan", "type": "Notification highlight color", "score": 0.9999328851699829},
    {"color": "Pink", "type": "Accent color", "score": 0.9999185800552368},
    {"color": "AliceBlue", "type": "Text color", "score": 0.999894380569458},
    {"color": "WhiteSmoke", "type": "Border color", "score": 0.9998866319656372},
    {"color": "Purple", "type": "Highlight color", "score": 0.9998842477798462},
    {"color": "Azure", "type": "Main color", "score": 0.9998782873153687},
    {"color": "AntiqueWhite", "type": "Alert color", "score": 0.9998581409454346},
    {"color": "DarkGray", "type": "Subtle background color", "score": 0.9996941089630127}
]

compiled_data = compile(pointer, data)
print("Compiled Data:")
print(compiled_data)

uncompiled_data = uncompile(compiled_data)
print("Uncompiled Data:")
print(uncompiled_data)
