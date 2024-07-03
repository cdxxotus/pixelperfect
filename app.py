from flask import Flask, request, jsonify
from PIL import Image
import base64
import io
import logging
import time
import torch
from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize text generation pipeline
generator = pipeline('text-generation', model='EleutherAI/gpt-neo-125M')

# Load the BLIP model
model_id = "Salesforce/blip-vqa-base"
processor = BlipProcessor.from_pretrained(model_id)
# Enable GPU/MPS device if available
device = "cuda" if torch.cuda.is_available() else "cpu"
device = "mps" if torch.backends.mps.is_available() else "cpu"
model = BlipForConditionalGeneration.from_pretrained(model_id).half().to(device)

@app.route('/predict', methods=['POST'])
def predict():
    start_time = time.time()  # Start measuring inference time

    try:
        data = request.json
        logging.info("Received data: %s", data)

        image_data = data.get('image_data')

        if not image_data:
            return jsonify({'error': 'image_data is required'}), 400

        # Process the image
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))
        optimized_size = (150, 150)
        image = image.resize(optimized_size)
        images = [image]

        inputs = processor(images=images, return_tensors="pt").to(device)

        with torch.inference_mode():  # Even better for inference optimization
            outputs = model.generate(**inputs, max_length=50, num_beams=1, do_sample=False)

        # Decode the generated tokens
        generated_texts = processor.batch_decode(outputs, skip_special_tokens=True)

        logging.info("Generated responses: %s", generated_texts)

        end_time = time.time()  # End measuring inference time
        inference_time = end_time - start_time
        logging.info(f"Inference time: {inference_time:.2f} seconds")

        return jsonify({'response': generated_texts, 'inference_time': inference_time})

    except Exception as e:
        logging.error("Error processing request: %s", e)
        return jsonify({'error': str(e)}), 500

@app.route('/get_home_screen_description', methods=['POST'])
def describe_ui():
    try:
        # Generate text for UI description
        prompt = "As EleutherAI, i want your today OS home screen to be:"
        generated_text = generator(prompt, do_sample=True, min_length=10, max_length=100)[0]['generated_text']

        logging.info("Generated UI description: %s", generated_text)

        return jsonify({'os_home_screen_description': generated_text})

    except Exception as e:
        logging.error("Error processing request: %s", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
