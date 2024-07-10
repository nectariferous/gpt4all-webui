document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const resetBtn = document.getElementById('reset-btn');
    const modelStatus = document.getElementById('model-status');

    sendBtn.addEventListener('click', sendMessage);
    resetBtn.addEventListener('click', resetConversation);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    function checkModelStatus() {
        fetch('/model-status')
            .then(response => response.json())
            .then(data => {
                if (data.initialized) {
                    modelStatus.textContent = 'Model Ready';
                    modelStatus.style.color = 'green';
                    sendBtn.disabled = false;
                } else {
                    modelStatus.textContent = 'Model Initializing...';
                    modelStatus.style.color = 'orange';
                    sendBtn.disabled = true;
                    setTimeout(checkModelStatus, 5000);  // Check again in 5 seconds
                }
            });
    }

    checkModelStatus();

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
                body: JSON.stringify({ 
                    prompt: message,
                    max_tokens: 1024,
                    temperature: 0.7,
                    top_k: 40,
                    top_p: 0.9,
                    repeat_penalty: 1.1
                }),
            });
            const data = await response.json();
            if (data.error) {
                addMessage('bot', `Error: ${data.error}`);
            } else {
                addMessage('bot', data.response);
                console.log(`Generation time: ${data.generation_time} seconds`);
            }
        } catch (error) {
            console.error('Error:', error);
            addMessage('bot', 'Sorry, I encountered an error while processing your request.');
        }
    }

    function resetConversation() {
        fetch('/reset', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                chatMessages.innerHTML = '';
                addMessage('bot', 'Conversation has been reset.');
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('bot', 'Sorry, I encountered an error while resetting the conversation.');
            });
    }
});