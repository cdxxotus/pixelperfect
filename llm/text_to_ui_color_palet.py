import json
from gliclass import GLiClassModel, ZeroShotClassificationPipeline
from transformers import AutoTokenizer
from pplang.compilers.python import main

types = [
    "Main color",
    "Secondary color",
    "Text color",
    "Highlight color",
    "Accent color",
    "Notification highlight color",
    "Subtle background color",
    "Border color",
    "Alert color",
    "Divider color"
]

file_path = 'datasets/color-names-100.json'

# Read and parse the JSON file
with open(file_path, 'r') as file:
    color_dict = json.load(file)

# Extract values to an array
color_names = list(color_dict.values())

# Create combined labels
combined_labels = [f"{color} - {type}" for color in color_names for type in types]

model = GLiClassModel.from_pretrained("knowledgator/gliclass-small-v1.0-lw")
tokenizer = AutoTokenizer.from_pretrained("knowledgator/gliclass-small-v1.0-lw")

pipeline = ZeroShotClassificationPipeline(model, tokenizer, classification_type='multi-label', device='cuda:0')

def get_colors_and_types_from_text(text, top_k=10):
    # Perform classification
    result = pipeline(text, combined_labels, threshold=0.5)

    # Debug print to check the structure of the result
    print("Pipeline Result:", result)

    # Ensure the result is not empty and is a dictionary
    if not result or not isinstance(result, list):
        print("Empty or invalid result")
        return json.dumps({"color_palet": []})

    # Extract labels and scores
    labels = [item['label'] for item in result[0]]
    scores = [item['score'] for item in result[0]]

    # Combine labels and scores into a list of tuples
    combined_results = list(zip(labels, scores))

    # Create a dictionary to hold the highest score for each type
    best_per_type = {type: (None, 0) for type in types}

    # Create a set to track unique colors
    unique_colors = set()

    # Iterate over combined results to find the highest score for each type
    for label, score in combined_results:
        color, type = label.split(" - ")
        if score > best_per_type[type][1] and color not in unique_colors:
            best_per_type[type] = (color, score)
            unique_colors.add(color)

    # Create a list of the best results per type
    top_colors_and_types = [{"color": color, "type": type, "score": score} for type, (color, score) in best_per_type.items() if color is not None]

    # Sort the final results by score in descending order
    top_colors_and_types = sorted(top_colors_and_types, key=lambda x: x['score'], reverse=True)

    # Ensure only one color per type and top 10 unique colors
    top_colors_and_types = top_colors_and_types[:top_k]

    # Debug print to check the final result
    print("Top Colors and Types:", top_colors_and_types)

    return main.compile("ui_color_palette_schema", top_colors_and_types)
