import json
from gliclass import GLiClassModel, ZeroShotClassificationPipeline
from transformers import AutoTokenizer

file_path = 'datasets/color-names-100.json'

# Read and parse the JSON file
with open(file_path, 'r') as file:
    color_dict = json.load(file)

# Extract values to an array
color_names = list(color_dict.values())

model = GLiClassModel.from_pretrained("knowledgator/gliclass-small-v1.0-lw")
tokenizer = AutoTokenizer.from_pretrained("knowledgator/gliclass-small-v1.0-lw")

pipeline = ZeroShotClassificationPipeline(model, tokenizer, classification_type='multi-label', device='cuda:0')

def get_colors_from_text(text, top_k=10):
    # Perform classification
    result = pipeline(text, color_names, threshold=0.5)
    
    # Debug prints to check the structure of the result
    print("Pipeline Result:", result)

    # Ensure the result is not empty and is a list
    if not result or not isinstance(result, list):
        return []

    # Access the first element of the result list
    classification_result = result[0]

    # Ensure the first element is a list of dictionaries with 'label' and 'score' keys
    if not classification_result or not isinstance(classification_result, list):
        return []

    # Extract labels and scores
    labels = [item['label'] for item in classification_result]
    scores = [item['score'] for item in classification_result]

    # Combine labels and scores into a list of tuples and sort by score
    sorted_result = sorted(zip(labels, scores), key=lambda x: x[1], reverse=True)
    
    # Select the top_k colors
    top_colors = sorted_result[:top_k]
    return top_colors
