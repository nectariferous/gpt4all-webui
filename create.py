import os
import sys

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

def create_file(path, content):
    with open(path, 'w') as file:
        file.write(content)
    print(f"Created file: {path}")

def main():
    # Create main directory structure
    create_directory('static')
    create_directory('static/css')
    create_directory('static/js')
    create_directory('templates')

    # Create app.py
    app_py_content = '''
from flask import Flask, render_template, request, jsonify
from gpt4all import GPT4All

app = Flask(__name__)

# Initialize the model
model = GPT4All("meta-llama/Llama-2-7b-chat-hf")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.json['prompt']
    max_tokens = request.json.get('max_tokens', 1024)
    
    with model.chat_session():
        response = model.generate(prompt, max_tokens=max_tokens)
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
'''
    create_file('app.py', app_py_content)

    # Create index.html
    index_html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GPT4All Web UI</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>GPT4All Web UI</h1>
        <div class="chat-container">
            <div id="chat-messages"></div>
            <div class="input-container">
                <textarea id="user-input" placeholder="Type your message here..."></textarea>
                <button id="send-btn">Send</button>
            </div>
        </div>
    </div>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
'''
    create_file('templates/index.html', index_html_content)

    # Create style.css
    style_css_content = '''
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    background-color: #f4f4f4;
}
.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}
h1 {
    text-align: center;
    color: #333;
}
.chat-container {
    background-color: #fff;
    border-radius: 5px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}
#chat-messages {
    height: 400px;
    overflow-y: auto;
    padding: 20px;
}
.message {
    margin-bottom: 15px;
    padding: 10px;
    border-radius: 5px;
}
.user-message {
    background-color: #e6f2ff;
    text-align: right;
}
.bot-message {
    background-color: #f0f0f0;
}
.input-container {
    display: flex;
    padding: 20px;
    background-color: #f9f9f9;
}
#user-input {
    flex-grow: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    resize: none;
}
#send-btn {
    padding: 10px 20px;
    background-color: #007bff;
    color: #fff;
    border: none;
    border-radius: 5px;
    margin-left: 10px;
    cursor: pointer;
}
#send-btn:hover {
    background-color: #0056b3;
}
'''
    create_file('static/css/style.css', style_css_content)

    # Create main.js
    main_js_content = '''
document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessage('user', message);
            userInput.value = '';
            fetchBotResponse(message);
        }
    }

    function addMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        messageElement.textContent = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function fetchBotResponse(message) {
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: message }),
            });
            const data = await response.json();
            addMessage('bot', data.response);
        } catch (error) {
            console.error('Error:', error);
            addMessage('bot', 'Sorry, I encountered an error while processing your request.');
        }
    }
});
'''
    create_file('static/js/main.js', main_js_content)

    # Create requirements.txt
    requirements_content = '''
flask==2.0.1
gpt4all==1.0.8
'''
    create_file('requirements.txt', requirements_content)

    # Create .replit file for Replit configuration
    replit_content = '''
language = "python3"
run = "python app.py"
'''
    create_file('.replit', replit_content)

    print("Project structure and files have been created successfully!")

if __name__ == "__main__":
    main()
