import os
import logging
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from gpt4all import GPT4All
from werkzeug.exceptions import InternalServerError
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Model configuration
MODEL_NAME = "ggml-gpt4all-j-v1.3-groovy.bin"
MODEL_PATH = os.path.join(os.path.expanduser("~"), ".cache", "gpt4all")
FULL_PATH = os.path.join(MODEL_PATH, MODEL_NAME)

# Global variable to store the model instance
model = None

def initialize_model():
    global model
    if not os.path.exists(FULL_PATH):
        logger.info(f"Downloading {MODEL_NAME}...")
        os.makedirs(MODEL_PATH, exist_ok=True)
        GPT4All.download_model(MODEL_NAME, MODEL_PATH)

    logger.info("Initializing model...")
    model = GPT4All(FULL_PATH)
    logger.info("Model initialized successfully.")

# Initialize model in a separate thread
threading.Thread(target=initialize_model).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if model is None:
        return jsonify({'error': 'Model is still initializing. Please try again in a moment.'}), 503

    data = request.json
    prompt = data['prompt']
    max_tokens = data.get('max_tokens', 1024)
    temperature = data.get('temperature', 0.7)
    top_k = data.get('top_k', 40)
    top_p = data.get('top_p', 0.9)
    repeat_penalty = data.get('repeat_penalty', 1.1)

    # Get or initialize conversation history
    if 'conversation' not in session:
        session['conversation'] = []

    # Add user message to conversation history
    session['conversation'].append({"role": "user", "content": prompt})

    # Construct full prompt from conversation history
    full_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in session['conversation']])

    try:
        start_time = time.time()
        response = model.generate(full_prompt, max_tokens=max_tokens, temp=temperature, 
                                  top_k=top_k, top_p=top_p, repeat_penalty=repeat_penalty)
        end_time = time.time()

        # Add model response to conversation history
        session['conversation'].append({"role": "assistant", "content": response})

        # Limit conversation history to last 10 messages
        session['conversation'] = session['conversation'][-10:]

        return jsonify({
            'response': response,
            'conversation': session['conversation'],
            'generation_time': round(end_time - start_time, 2)
        })

    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise InternalServerError("An error occurred while generating the response.")

@app.route('/reset', methods=['POST'])
def reset_conversation():
    session.pop('conversation', None)
    return jsonify({'message': 'Conversation reset successfully.'})

@app.errorhandler(InternalServerError)
def handle_internal_server_error(e):
    return jsonify({'error': str(e)}), 500

@app.route('/model-status', methods=['GET'])
def model_status():
    return jsonify({'initialized': model is not None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)