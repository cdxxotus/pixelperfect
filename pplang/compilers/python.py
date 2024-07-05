import logging
import json
import re
import time

# Configure logging
logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')

# Use a dictionary to store pointers
pointers_names = {}
unicode_map = []
reserved_chars = set()
unicode_to_index = {}

def load_reserved_chars(filename):
    try:
        with open(filename, 'r') as file:
            for line in file:
                reserved_chars.update(line.strip())
    except FileNotFoundError:
        logging.error(f"Reserved characters file not found: {filename}")

def load_unicode_map(filename):
    try:
        with open(filename, 'r') as file:
            unicode_map.extend(file.read().strip())
        for idx, char in enumerate(unicode_map):
            unicode_to_index[char] = idx
    except FileNotFoundError:
        logging.error(f"Unicode map file not found: {filename}")

load_reserved_chars("pplang/hard/reserved")
load_unicode_map("pplang/hard/unicodes")

def ensure_size(lst, index):
    if len(lst) <= index:
        lst.extend([None] * (index + 1 - len(lst)))

def get_dictionary(pointer):
    dictionary = {}
    dictionary_pixels = []
    seen_pixels = set()
    try:
        with open(f"pplang/pointers/{pointer}", 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():  # Ensure we skip empty lines
                    pixel = line[0]
                    human = line.strip()[1:]
                    if pixel in seen_pixels:
                        logging.warning(f"Duplicate Unicode found: {pixel}. Skipping entry: {human}")
                    else:
                        dictionary[human] = pixel
                        dictionary_pixels.append(pixel)
                        seen_pixels.add(pixel)
        logging.debug(f"Dictionary: {dictionary}")
        logging.debug(f"Dictionary Pixels: {dictionary_pixels}")
        return dictionary, dictionary_pixels
    except FileNotFoundError:
        logging.error(f"Pointer file not found: {pointer}")
        return {}, []

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
    logging.debug(f"parsechemabefore:{schema}")
    formatted_string = schema.replace("{", '{"').replace("}", '"}').replace(":", '": "').replace(",", '", "')
    logging.debug(f"formatted_string:{formatted_string}")
    if formatted_string[0] == "[" or formatted_string[0] == "{":
        try:
            return json.loads(formatted_string)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse schema: {e}")
            return {}
    else:
        return formatted_string

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

def translate_with_priority(big_string, translations):
    # Split the big_string by any whitespace while preserving the whitespace
    words = re.split(r'(\s+)', big_string)
    
    # Debug print to show the split words
    logging.debug(f"Split words: {words}")
    
    # Sort dictionary keys by length in descending order
    sorted_keys = sorted(translations.keys(), key=len, reverse=True)

    # Create a list to store the translated words
    encoded = ""

    # Iterate over each word in the split string
    for word in words:
        matched = False
        # Try to match and replace using the sorted keys
        for key in sorted_keys:
            if word == key:
                logging.debug(f"Translating: {word} -> {translations[key]}")
                encoded+=f"{(translations[key].strip())}¡"
                matched = True
                break
        if not matched:
            encoded+=f"{(word.strip())}¡"
    
    return encoded


def process_object(schema, obj):
    self_pointers_pos = {}

    logging.debug(f"process_object:schema,obj::{schema.__class__}:{obj}")
    if isinstance(schema, list):
        compiled_result = []
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
    elif isinstance(schema, dict):
        compiled_item = [None] * len(schema)
        idx = 0
        for key, value in schema.items():
            # print(f"key:value:::{key}:{value}")
            if value in obj or value[0] == "+":
                if idx == 0:
                    self_pointers_pos[key] = {}
                if value[0] == "+":
                    const_names = get_pointer_names("+")
                    item_key = const_names[int(value[1:])]
                    item_value = obj[item_key]
                else:
                    item_value = obj[value]
                if key == "*":
                    compiled_item[idx] = f"*({item_value})"
                elif key[0] == "+":
                    compiled_item[idx] = f"({item_value})"
                elif key[0]=="@":
                    light_to_shadow=item_value.replace(" ", "¦¦")
                    compiled_item[idx] = f"({light_to_shadow})"
                else:
                    key_pointer_index = get_pointer_pos(self_pointers_pos, key, item_value)
                    compiled_item[idx] = key_pointer_index
                idx += 1

        return compiled_item
    elif schema == "@":
        dictionary, dictionary_pixels = get_dictionary(schema)
        print(f"obj: {obj}")
        shadowspaces=obj.replace(" ", "​")
        translated = ''.join(translate_with_priority(shadowspaces, dictionary))  # Ensure generator is fully consumed
        return translated

def get_reverse_dictionary(dictionary):
    if isinstance(dictionary, dict):
        reverse_dict = {v: k for k, v in dictionary.items()}
        logging.debug(f"Reverse Dictionary: {reverse_dict}")
        return reverse_dict
    else:
        raise ValueError("Input is not a dictionary")

def reverse_translate_with_priority(encoded_string, translations):
    # Create a reverse dictionary for translations
    reverse_translations = {v: k for k, v in translations.items()}

    # Split the encoded_string by the custom delimiter
    words = encoded_string.split('*%*')

    # Sort reverse dictionary keys by length in descending order
    sorted_keys = sorted(reverse_translations.keys(), key=len, reverse=True)

    # Create a list to store the decoded words
    decoded_words = []

    # Iterate over each word in the split string
    for word in words:
        matched = False
        # Try to match and replace using the sorted reverse keys
        for key in sorted_keys:
            if word == key:
                logging.debug(f"Reverse Translating: {word} -> {reverse_translations[key]}")
                decoded_words.append(reverse_translations[key])
                matched = True
                break
        if not matched:
            # If no match, keep the original word
            decoded_words.append(word)

    # Join the decoded words back into a single string with spaces
    decoded_string = ' '.join(decoded_words)
    return decoded_string

def reverse_compiled_string(compiled_string, pointer):
    dictionary, dictionary_pixels = get_dictionary(pointer)
    
    return reverse_translate_with_priority(compiled_string,dictionary)

def next_char(compiled_str):
    for char in compiled_str:
        yield char

def jump_to_next_schema(char_gen):
    substring = ""
    for char in char_gen:
        if char == "$":
            return substring
        substring += char
    return substring  # In case no more "$" is found, return the remaining substring

def compile(pointer, obj):
    start_time = time.time()

    schema_pointers_names = get_pointer_names(pointer)
    schema_pointer_pos = get_pointer_pos({}, "=", pointer)

    raw_schema = schema_pointers_names[0] if schema_pointers_names else ""
    schema = parse_schema(raw_schema)

    logging.debug(f"schema:{schema}")
    logging.debug(f"obj:{obj}")

    processed_obj = process_object(schema, obj)
    stringified_obj = f"{processed_obj}"
    stringified_obj = stringified_obj.replace("\\'", "'")

    if stringified_obj[0] == "[" and stringified_obj[1] != "[":
        stringified_obj = replace_at_index(stringified_obj, 0, "{")
        stringified_obj = replace_at_index(stringified_obj, len(stringified_obj) - 1, "}")

    compiled_result = f"${schema_pointer_pos}{stringified_obj}".replace('\\\\', '\\').replace("'*", "*").replace("'`", "`").replace("`'", "`").replace(" ", "").replace("None", "-").replace("],[", '|').replace("[[", "[").replace("]]", "]").replace(")'", ")").replace("'(", "(")

    # Regex to match digits that are not part of floating point numbers
    parts = re.split(r'(?<!\\)(\d+\.\d+|\d+|.)', compiled_result)
    unicode_result = ''.join(convert_num(part) if part.isdigit() else part for part in parts if part)

    end_time = time.time()
    logging.warning(f"Compilation time: {end_time - start_time:.6f} seconds")

    return unicode_result, end_time - start_time

def uncompile(compiled_str):
    start_time = time.time()

    shadow_to_light_str=compiled_str.replace("¦¦", " ")
    char_gen = next_char(shadow_to_light_str)
    decoded_data = ""
    is_escaped = False
    schema = []
    parent_schema = []
    first_schema = []
    current_operation = ""
    x_schema = 0
    x_object = 0
    decoding_up_to = ""
    in_nested_build = False
    decodeding_up_to = ""

    for char in char_gen:
        # print(f"decoded_data:{decoded_data}")
        # print(f"schema:{schema}")
        # print(f"parent_schema:{parent_schema}")
        # print(f"decodeding_up_to:{decodeding_up_to}")
        # print(f"last-currentoperation:{current_operation}")
        # print(f"xobject:{x_object}")
        decoding_up_to += char
        if char == '\\' and not is_escaped:
            is_escaped = True
        elif char == "{" and not is_escaped:
            x_object = 0
            decoded_data += char
            current_operation = "{"
        elif char == "}" and not is_escaped:
            decoded_data += char
        elif char == "(" and not is_escaped:
            if not in_nested_build:
                key = list(schema[0].keys())[x_object]
                if schema[0][key][0] == "+":
                    pointer_name = get_pointer_names("+")[int(schema[0][key][1:])]
                    decoded_data += f"\"{pointer_name}\":\""
                else:
                    decoded_data += f"\"{schema[0][key]}\":\""
                current_operation = "("
        elif char == ")" and not is_escaped:
            if in_nested_build:
                schema = parent_schema
                in_nested_build = False
            else:
                decoded_data += "\""
        elif char == '$' and not is_escaped:
            x_object = 0
            current_operation = "$"
        elif char == "[" and not is_escaped:
            x_object = 0
            decoded_data += char
            current_operation = "[{"
        elif char == ',' and not is_escaped:
            decoded_data += char
            x_object += 1
        elif char == ']' and not is_escaped:
            if current_operation == "{":
                decoded_data += f"}}{char}"
            else:
                decoded_data += char
            current_operation = "{"
            x_object = 0
        elif char == '|' and not is_escaped:
            if current_operation == "{":
                decoded_data += "},{"
            else:
                decoded_data += "],["
            x_object = 0
            current_operation = "{"
        # elif char == '@' and not is_escaped:
        #     current_operation = "@"
        else:
            is_escaped = False
            pos = int(unicode_to_index.get(char, -1))

            if current_operation == "$":
                schema_list_pointers_names = get_pointer_names("=")
                schema_name = schema_list_pointers_names[pos]
                raw_schema = get_pointer_names(schema_name)[0]
                unknown_schema = parse_schema(raw_schema)
                parent_schema = schema
                if isinstance(unknown_schema, dict):
                    schema = [unknown_schema]
                else:
                    schema = unknown_schema
                if len(first_schema) == 0:
                    ensure_size(first_schema, 0)
                    first_schema[0] = schema
                if schema[0] == "@":
                    current_operation = "@"
                    decoded_data += "\""
                else:
                    current_operation = ""
            elif current_operation == "(":
                decoded_data += char
            elif current_operation == "[{":
                key = list(schema[0].keys())[x_object]
                if char == "-":
                    decoded_data += f"{{\"{schema[0][key]}\":null"
                else:
                    pointer_names = get_pointer_names(key)
                    pointer_name = pointer_names[pos] if len(pointer_names) > pos else "null"
                    decoded_data += f"{{\"{schema[0][key]}\":\"{pointer_name}\""
                current_operation = "{"
            elif current_operation == "{":
                key = list(schema[0].keys())[x_object]
                if char == "-":
                    decoded_data += f"\"{schema[0][key]}\":null"
                elif char == "*":
                    in_nested_build = True
                    decoded_data += f"\"{schema[0][key]}\":"
                else:
                    pointer_names = get_pointer_names(key)
                    pointer_name = pointer_names[pos] if len(pointer_names) > pos else "null"
                    decoded_data += f"\"{schema[0][key]}\":\"{pointer_name}\""
            elif current_operation == "@":
                substring = jump_to_next_schema(char_gen)
                translation = ''.join(reverse_compiled_string(char + substring, "@"))
                decoded_data += translation

    decoded_data = ''.join(decoded_data)
    compiled_results = decoded_data

    if isinstance(first_schema[0], dict) or isinstance(first_schema[0], list):
        try:
            compiled_results = json.loads(decoded_data)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse decoded data: {e}")
            return None, 0

    end_time = time.time()
    logging.warning(f"Uncompilation time: {end_time - start_time:.6f} seconds")

    return compiled_results, end_time - start_time

def calculate_compression_rate(original, compiled):
    original_size = len(original.encode('utf-8'))
    compiled_size = len(compiled.encode('utf-8'))
    compression_rate = (1 - (compiled_size / original_size)) * 100
    return compression_rate

def convert_num(num):
    if num.isdigit():
        index = int(num)
        if 0 <= index < len(unicode_map):
            unicode_char = unicode_map[index]
            if unicode_char in reserved_chars:
                return f"\\{unicode_char}"
            return unicode_char
    return num

def replace_at_index(s, index, replacement):
    # Check if the index is within the valid range
    if index < 0 or index >= len(s):
        raise IndexError("Index out of range")
    # Create a new string with the replacement
    return s[:index] + replacement + s[index+1:]


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

data_color_palet_response = {
    "color_palet": """$\$[¾,"|ʹ,&|ャ,%|-,#|-,\(|両,\$|~,!|-,\)|-,']""",
    "inference_time": 2.1053810119628906,
}

data_os_desciripn = {'os_home_screen_description': "qsdfqsdf qs qsdf qsdf qsdf qsd qq qsf", 'inference_time': 1.343}

data_string = """
Vous pouvez partager un article en cliquant sur les icônes de partage en haut à droite de celui-ci. 
La reproduction totale ou partielle d’un article, sans l’autorisation écrite et préalable du Monde, est strictement interdite. 
Pour plus d’informations, consultez nos conditions générales de vente. 
Pour toute demande d’autorisation, contactez syndication@lemonde.fr. 
En tant qu’abonné, vous pouvez offrir jusqu’à cinq articles par mois à l’un de vos proches grâce à la fonctionnalité « Offrir un article ». 

https://www.lemonde.fr/politique/live/2024/07/04/en-direct-legislatives-2024-plus-de-3-1-millions-de-procurations-sur-l-ensemble-des-scrutins_6245747_823448.html

Le préfet de police de Paris, Laurent Nuñez, va interdire une manifestation du collectif Action antifasciste Paris-Banlieue prévue dimanche devant l’Assemblée nationale à la clôture du second tour des législatives, a rapporté jeudi soir à l’Agence France-Presse une source policière.

Ce collectif a appelé dans un post sur X à un rassemblement « dimanche à 20 h devant l’Assemblée nationale quelle que soit l’issue » du scrutin. « Aujourd’hui plus que jamais, faisons bloc par tous les moyens contre l’extrême droite et ses alliés », a-t-il fait valoir. Sur les réseaux sociaux, le collectif a lancé un appel à « converger vers l’Assemblée nationale ».

Le ministre de l’intérieur, Gérald Darmanin, a annoncé jeudi que « 30 000 policiers et gendarmes, dont 5 000 à Paris et sa banlieue » seraient mobilisés dimanche soir pour le second tour du scrutin législatif anticipé. Les services de renseignement considèrent, selon une source policière, qu’il existe « de réels risques de troubles à l’ordre public après le second tour avec à la fois des rassemblements qui pourraient donner lieu à des incidents mais aussi des risques d’affrontements entre des groupes antagonistes ».
"""

compiled_data, compile_time = compile(pointer, data)
print("Compiled Data:")
print(compiled_data)

uncompiled_data, uncompile_time = uncompile(compiled_data)
print("Uncompiled Data:")
print(uncompiled_data)

compiled_colorpaletresponse_data, _ = compile("ui_color_palette_response", data_color_palet_response)
print("Compiled ColorPaletResponse Data:")
print(compiled_colorpaletresponse_data)

uncompiled_colorpaletresponse_data, _ = uncompile(compiled_colorpaletresponse_data)
print("Uncompiled ColorPaletResponse Data:")
print(uncompiled_colorpaletresponse_data)

compiled_data_os, compile_time_os = compile("os_home_screen_description_response", data_os_desciripn)
print("Compiled Data_os:")
print(compiled_data_os)

uncompiled_data_os, uncompile_time_os = uncompile(compiled_data_os)
print("Uncompiled Data_os:")
print(uncompiled_data_os)

compiled_string, compile_string_time = compile("string", data_string)
print("Compiled String Data:")
print(compiled_string)
print("Original String Data:", data_string)

uncompiled_string, uncompile_string_time = uncompile(compiled_string)
print("Uncompiled String Data:")
print(uncompiled_string)

# Calculate compression rates
compression_rate_data = calculate_compression_rate(str(uncompiled_data), compiled_data)
compression_rate_colorpaletresponse = calculate_compression_rate(str(uncompiled_colorpaletresponse_data), compiled_colorpaletresponse_data)
compression_rate_string = calculate_compression_rate(str(uncompiled_string), compiled_string)

print(f"Compression Rate (data): {compression_rate_data:.2f}%")
print(f"Compression Rate (color_palet_response): {compression_rate_colorpaletresponse:.2f}%")
print(f"Compression Rate (string): {compression_rate_string:.2f}%")

print(f"Compilation time for data: {compile_time:.6f} seconds")
print(f"Uncompilation time for data: {uncompile_time:.6f} seconds")
print(f"Compilation time for string: {compile_string_time:.6f} seconds")
print(f"Uncompilation time for string: {uncompile_string_time:.6f} seconds")
