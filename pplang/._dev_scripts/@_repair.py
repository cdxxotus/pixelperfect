import re
import os
import shutil
from collections import defaultdict
from datetime import datetime
import random

# Function to create a backup of the file
def create_backup(file_path):
    backup_path = f"{file_path}.bak"
    shutil.copy(file_path, backup_path)
    print(f"Backup created at {backup_path}")

# Function to read the input file
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()
    
# Function to write updated lines back to the file
def write_file(file_path, lines):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Updated file has been saved.")

# Function to create a backup of the file
def create_backup(file_path):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_dir = os.path.join(os.path.dirname(file_path), '.retired')
    os.makedirs(backup_dir, exist_ok=True)
    backup_file_path = os.path.join(backup_dir, f'{os.path.basename(file_path)}.{timestamp}')
    shutil.copy2(file_path, backup_file_path)

# Function to display and handle duplicate translations one by one
def handle_duplicates_one_by_one(emoji, texts, line_indices):
    updated_texts = texts[:]
    line_indices_to_delete = []

    for idx, text in enumerate(texts):
        print(f"\n{emoji} has the following translations:")
        for idx, text in enumerate(updated_texts):
            print(f"{idx}: {text}")

        action = input(f"Choose action for {emoji} translation '{text}': (delete/add/edit/skip/auto-repair/back): ").strip().lower()

        if action == 'back':
            return updated_texts, line_indices_to_delete
        if action == 'delete':
            line_indices_to_delete.append(line_indices[idx])
            updated_texts.remove(text)
        elif action == 'add':
            new_translation = input("Enter new translation to add: ").strip()
            if new_translation:
                updated_texts.append(new_translation)
        elif action == 'edit':
            new_translation = input("Enter new translation: ").strip()
            if new_translation:
                updated_texts[idx] = new_translation
        elif action == 'auto-repair':
            updated_texts, line_indices_to_delete = auto_repair(updated_texts, emoji, line_indices)
        elif action == 'skip':
            continue

    return updated_texts, line_indices_to_delete

# Function to list all duplicates and handle edit/add/delete
def handle_duplicates_list_all(emoji_dict, line_indices_dict):
    emojis_with_duplicates = {emoji: texts for emoji, texts in emoji_dict.items() if len(set(texts)) < len(texts)}

    if not emojis_with_duplicates:
        print("No duplicates found.")
        return emoji_dict, []

    print("Emojis with duplicates:")
    for idx, emoji in enumerate(emojis_with_duplicates):
        print(f"{idx}: {emoji}")

    choice = input("Enter the ID of the emoji to edit, add, or delete translations (or 'back' to go back): ").strip().lower()
    if choice == 'back':
        return emoji_dict, []

    selected_emoji = list(emojis_with_duplicates.keys())[int(choice)]
    texts = emoji_dict[selected_emoji]
    line_indices = line_indices_dict[selected_emoji]
    line_indices_to_delete = []

    print(f"\n{selected_emoji} has the following translations:")
    for idx, text in enumerate(texts):
        print(f"{idx}: {text}")

    while True:
        action = input("Choose action: (delete/add/edit/done/auto-repair/back/save): ").strip().lower()
        if action == 'back':
            break
        if action == 'save':
            save_changes = input("Do you want to save changes? (yes/no): ").strip().lower()
            if save_changes == 'yes':
                return emoji_dict, line_indices_to_delete
        if action == 'delete':
            ids_to_delete = input("Enter the IDs of translations to delete, separated by commas: ")
            if ids_to_delete:
                ids_to_delete = list(map(int, ids_to_delete.split(',')))
                for idx in sorted(ids_to_delete, reverse=True):
                    if 0 <= idx < len(texts):
                        texts.pop(idx)
                        line_indices_to_delete.append(line_indices[idx])
        elif action == 'add':
            new_translation = input("Enter new translation to add: ").strip()
            if new_translation:
                texts.append(new_translation)
        elif action == 'edit':
            id_to_edit = int(input("Enter the ID of the translation to edit: "))
            if 0 <= id_to_edit < len(texts):
                new_translation = input("Enter new translation: ").strip()
                if new_translation:
                    texts[id_to_edit] = new_translation
        elif action == 'auto-repair':
            texts, line_indices_to_delete = auto_repair(texts, selected_emoji, line_indices)
        elif action == 'done':
            break

    emoji_dict[selected_emoji] = texts
    return emoji_dict, line_indices_to_delete

# Function to list translations that could be faux-amis and handle edit/add/delete
def handle_faux_amis(emoji_dict, line_indices_dict):
    all_translations = defaultdict(list)

    # Collect all translations and their corresponding emojis
    for emoji, texts in emoji_dict.items():
        for text in texts:
            all_translations[text].append(emoji)

    # Filter translations that have multiple corresponding emojis
    faux_amis_candidates = {text: emojis for text, emojis in all_translations.items() if len(emojis) > 1}

    if not faux_amis_candidates:
        print("No faux-amis candidates found.")
        return emoji_dict, []

    print("Faux-amis candidates:")
    for idx, text in enumerate(faux_amis_candidates):
        print(f"{idx}: {text}")

    choice = input("Enter the ID of the translation to edit, add, or delete from its unicode parent (or 'back' to go back): ").strip().lower()
    if choice == 'back':
        return emoji_dict, []

    selected_text = list(faux_amis_candidates.keys())[int(choice)]
    associated_emojis = faux_amis_candidates[selected_text]

    print(f"\nThe translation '{selected_text}' is associated with the following emojis:")
    for idx, emoji in enumerate(associated_emojis):
        print(f"{idx}: {emoji}")

    emoji_choice = int(input("Enter the ID of the emoji you want to modify: "))
    selected_emoji = associated_emojis[emoji_choice]
    texts = emoji_dict[selected_emoji]
    line_indices = line_indices_dict[selected_emoji]
    line_indices_to_delete = []

    while True:
        action = input("Choose action: (delete/add/edit/done/auto-repair/back/save): ").strip().lower()
        if action == 'back':
            break
        if action == 'save':
            save_changes = input("Do you want to save changes? (yes/no): ").strip().lower()
            if save_changes == 'yes':
                return emoji_dict, line_indices_to_delete
        if action == 'delete':
            idx_to_delete = texts.index(selected_text)
            texts.pop(idx_to_delete)
            line_indices_to_delete.append(line_indices[idx_to_delete])
        elif action == 'add':
            new_translation = input("Enter new translation to add: ").strip()
            if new_translation:
                texts.append(new_translation)
        elif action == 'edit':
            idx_to_edit = texts.index(selected_text)
            new_translation = input("Enter new translation: ").strip()
            if new_translation:
                texts[idx_to_edit] = new_translation
        elif action == 'auto-repair':
            texts, line_indices_to_delete = auto_repair(texts, selected_emoji, line_indices)
        elif action == 'done':
            break

    emoji_dict[selected_emoji] = texts
    return emoji_dict, line_indices_to_delete

# Function to create a duplicate translation
def create_duplicate(emoji, texts):
    new_translation = input(f"Enter new duplicate translation for {emoji}: ").strip()
    if new_translation:
        texts.append(new_translation)
    return texts

# Function to generate a unique Unicode character
def generate_unique_unicode(emoji_dict):
    existing_unicodes = set(emoji_dict.keys())
    
    # Range of Unicode characters to choose from
    unicode_start = 0x1F300  # Starting point of Unicode block for emojis
    unicode_end = 0x1F5FF  # Ending point of Unicode block for emojis

    while True:
        new_unicode = chr(random.randint(unicode_start, unicode_end))
        if new_unicode not in existing_unicodes:
            return new_unicode

# Function to repair all duplicates by making unicodes unique
def repair_all(emoji_dict, lines, line_indices_dict):
    existing_unicodes = set(emoji_dict.keys())
    new_emoji_dict = defaultdict(list)
    new_lines = lines[:]

    for emoji, texts in emoji_dict.items():
        unique_emoji = emoji
        for text, line_index in zip(texts, line_indices_dict[emoji]):
            # If the text already exists in new_emoji_dict, generate a new unique Unicode
            if any(text in new_texts for new_texts in new_emoji_dict.values()):
                while unique_emoji in existing_unicodes:
                    unique_emoji = generate_unique_unicode(new_emoji_dict)
                new_emoji_dict[unique_emoji].append(text)
                existing_unicodes.add(unique_emoji)
                # Update the line in the original file content
                new_lines[line_index] = unique_emoji + " " + text + "\n"
            else:
                new_emoji_dict[unique_emoji].append(text)
                existing_unicodes.add(unique_emoji)

    return new_emoji_dict, new_lines

# Function to auto-repair duplicates within a specific unicode
def auto_repair(texts, emoji, line_indices):
    new_texts = []
    new_indices_to_delete = []
    for idx, text in enumerate(texts):
        if texts.count(text) > 1:
            new_texts.append(text)
            new_indices_to_delete.append(line_indices[idx])
    return new_texts, new_indices_to_delete

# Function to strip extra white spaces between the first char (unicode) and translation
def strip_extra_whitespaces(lines):
    updated_lines = []
    for line in lines:
        # Check if the line has at least two characters
        if len(line) > 1 and line[1] == ' ':
            # Remove the whitespace at position [1]
            updated_line = line[0] + line[2:]
            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)
    return updated_lines

# Prompt the user for the concept they want to manipulate
def choose_concept():
    print("Choose the concept you want to manipulate:")
    print("1. Duplicates and faux-amis")
    print("2. Strip extra white spaces")
    choice = input("Enter the number of your choice: ")
    return choice

# Prompt the user for the duplicate handling method
def choose_duplicate_method():
    print("Choose how you want to handle duplicates:")
    print("1. Verify one by one")
    print("2. List all duplicate unicodes")
    print("3. Create a duplicate")
    print("4. List translations that could be faux-amis")
    print("5. Repair all")
    choice = input("Enter the number of your choice: ")
    return choice

# Function to save the updated file
def save_updated_file(file_path, lines_to_delete, lines):

    lines_to_delete = set(lines_to_delete)
    updated_lines = [line for index, line in enumerate(lines) if index not in lines_to_delete]

    # Create a backup before writing
    create_backup(file_path)

    # Write the updated lines back to the file
    write_file(file_path, updated_lines)

# Updated extraction logic to get the first Unicode character of the line
def extract_first_unicode_character(lines):
    emoji_dict = defaultdict(list)
    line_indices_dict = defaultdict(list)
    
    for index, line in enumerate(lines):
        first_char = line[0]
        remaining_text = line[1:].strip()
        if remaining_text:  # Only process non-empty lines
            emoji_dict[first_char].append(remaining_text)
            line_indices_dict[first_char].append(index)

    return emoji_dict, line_indices_dict

# File path to read from
file_path = 'pointers/@'  # Replace with your file path

# Read the input text from the file
lines = read_file(file_path)

# Prompt the user for the concept they want to manipulate
concept_choice = choose_concept()

if concept_choice == '1':
    # Extract the first Unicode character and the corresponding text
    emoji_dict, line_indices_dict = extract_first_unicode_character(lines)

    # Track lines to delete
    lines_to_delete = []

    # Handle duplicates and faux-amis based on the chosen method
    duplicate_method_choice = choose_duplicate_method()
    if duplicate_method_choice == '1':
        for emoji, texts in emoji_dict.items():
            if len(set(texts)) < len(texts):
                updated_texts, line_indices_to_delete = handle_duplicates_one_by_one(emoji, texts, line_indices_dict[emoji])
                emoji_dict[emoji] = updated_texts
                lines_to_delete.extend(line_indices_to_delete)
    elif duplicate_method_choice == '2':
        emoji_dict, line_indices_to_delete = handle_duplicates_list_all(emoji_dict, line_indices_dict)
        lines_to_delete.extend(line_indices_to_delete)
    elif duplicate_method_choice == '3':
        for emoji, texts in emoji_dict.items():
            updated_texts = create_duplicate(emoji, texts)
            emoji_dict[emoji] = updated_texts
    elif duplicate_method_choice == '4':
        emoji_dict, line_indices_to_delete = handle_faux_amis(emoji_dict, line_indices_dict)
        lines_to_delete.extend(line_indices_to_delete)
    elif duplicate_method_choice == '5':
        emoji_dict, updated_lines = repair_all(emoji_dict, lines, line_indices_dict)
        lines = updated_lines  # Update lines with the repaired content

    save_updated_file(file_path, lines_to_delete, lines)

elif concept_choice == '2':
    # Strip extra white spaces
    lines = strip_extra_whitespaces(lines)
    save_updated_file(file_path, [], lines)
else:
    print("Invalid choice.")
