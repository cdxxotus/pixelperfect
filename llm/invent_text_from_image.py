from flask import jsonify
import logging
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load the BLIP model
model_id = "Salesforce/blip-vqa-base"
processor = BlipProcessor.from_pretrained(model_id)
# Enable GPU/MPS device if available
device = "cuda" if torch.cuda.is_available() else "cpu"
device = "mps" if torch.backends.mps.is_available() else "cpu"
model = BlipForConditionalGeneration.from_pretrained(model_id).half().to(device)

def invent_text_from_image(image):
    try:
        optimized_size = (150, 150)
        image = image.resize(optimized_size)
        images = [image]

        inputs = processor(images=images, return_tensors="pt").to(device)

        with torch.inference_mode():  # Even better for inference optimization
            outputs = model.generate(**inputs, max_length=50, num_beams=1, do_sample=False)

        # Decode the generated tokens
        generated_texts = processor.batch_decode(outputs, skip_special_tokens=True)

        return generated_texts

    except Exception as e:
        logging.error("Error processing request: %s", e)
        return jsonify({'error': str(e)}), 500
