from flask import jsonify
import logging
import time
from transformers import pipeline
from pplang.compilers import object_to_pplang

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize text generation pipeline
generator = pipeline('text-generation', model='EleutherAI/gpt-neo-125M')

def get_home_screen_description():
    try:
        # Generate text for UI description
        prompt = "As EleutherAI, I want your today's OS home screen to be:"
        generated_text = generator(prompt, do_sample=True, min_length=10, max_length=100)[0]['generated_text']

        return generated_text

    except Exception as e:
        logging.error("Error processing request: %s", e)
        return jsonify({'error': str(e)}), 500
