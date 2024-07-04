import random

def generate_unicode_characters_by_family():
    unicode_families = {
        "Basic Latin": (0x0020, 0x007F),  # Basic Latin
        "Latin-1 Supplement": (0x00A0, 0x00FF),  # Latin-1 Supplement
        "Latin Extended-A": (0x0100, 0x017F),  # Latin Extended-A
        "Latin Extended-B": (0x0180, 0x024F),  # Latin Extended-B
        "Greek and Coptic": (0x0370, 0x03FF),  # Greek and Coptic
        "Cyrillic": (0x0400, 0x04FF),  # Cyrillic
        "Hebrew": (0x0590, 0x05FF),  # Hebrew
        "Arabic": (0x0600, 0x06FF),  # Arabic
        "Devanagari": (0x0900, 0x097F),  # Devanagari
        "Hiragana": (0x3040, 0x309F),  # Hiragana
        "Katakana": (0x30A0, 0x30FF),  # Katakana
        "CJK Unified Ideographs": (0x4E00, 0x9FFF),  # CJK Unified Ideographs
        "Emojis - Miscellaneous Symbols and Pictographs": (0x1F300, 0x1F5FF),  # Miscellaneous Symbols and Pictographs (Emojis)
        "Emojis - Emoticons": (0x1F600, 0x1F64F),  # Emoticons (Emojis)
        "Emojis - Supplemental Symbols and Pictographs": (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs (Emojis)
    }
    
    with open('unicodes.txt', 'w', encoding='utf-8') as file:
        for family, (start, end) in unicode_families.items():
            characters = []
            for code_point in range(start, end + 1):
                try:
                    characters.append(chr(code_point))
                except ValueError:
                    continue
            line = ''.join(characters)
            print(f"{family}: {line}")
            file.write(f"{line}\n")

# Generate and save Unicode characters by family
generate_unicode_characters_by_family()
