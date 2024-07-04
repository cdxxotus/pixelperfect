from flask import Flask, request, jsonify
from PIL import Image
import base64
import io
import logging
import time
import json
from llm.text_to_ui_color_palet import get_colors_and_types_from_text
from llm.invent_text_from_image import invent_text_from_image
from llm.get_home_screen_description import get_home_screen_description
from pplang.compilers import object_to_pplang

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.route('/invent_text_from_image', methods=['POST'])
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

        # Decode the generated tokens
        generated_texts = invent_text_from_image(image)

        logging.info("Generated responses: %s", generated_texts)

        end_time = time.time()  # End measuring inference time
        inference_time = end_time - start_time
        logging.info(f"Inference time: {inference_time:.2f} seconds")

        return jsonify({'text': generated_texts, 'inference_time': inference_time})

    except Exception as e:
        logging.error("Error processing request: %s", e)
        return jsonify({'error': str(e)}), 500

@app.route('/get_home_screen_description', methods=['POST'])
def describe_ui():
    start_time = time.time()  # Start measuring inference time

    try:
        generated_text = get_home_screen_description()

        logging.info("Generated UI description: %s", generated_text)

        end_time = time.time()  # End measuring inference time
        inference_time = end_time - start_time
        logging.info(f"Inference time: {inference_time:.2f} seconds")

        return json.dumps({'os_home_screen_description': generated_text, 'inference_time': inference_time}, indent=4)

    except Exception as e:
        logging.error("Error processing request: %s", e)
        return jsonify({'error': str(e)}), 500

@app.route('/get_colors_from_text', methods=['POST'])
def text_to_color():
    start_time = time.time()  # Start measuring inference time

    try:
        data = request.json
        logging.info("Received data for text to color: %s", data)

        if not data:
            return jsonify({'error': 'No data received'}), 400

        text = data.get('text')

        if not text:
            return jsonify({'error': 'text is required'}), 400

        color_palet = get_colors_and_types_from_text(text)

        logging.info("Generated color palette: %s", color_palet)

        end_time = time.time()  # End measuring inference time
        inference_time = end_time - start_time
        logging.info(f"Inference time: {inference_time:.2f} seconds")

        return object_to_pplang.compile("ui_color_palette_response", {"color_palet": color_palet, 'inference_time': inference_time})

    except Exception as e:
        logging.error("Error processing request: %s", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
