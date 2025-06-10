from flask import Flask, request
from flask_socketio import SocketIO, emit
import ollama
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Initialize Ollama client
# The OLLAMA_HOST environment variable will be set in the Dockerfile or docker-compose.yml
# Defaults to local Ollama if not set.
ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
ollama_client = ollama.Client(host=ollama_host)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral") # Default model

def get_ollama_response(user_message: str):
    """
    Sends a message to Ollama and returns the response.
    """
    try:
        print(f"Sending to Ollama model {OLLAMA_MODEL} at {ollama_host}: {user_message}")
        response = ollama_client.chat(
            model=OLLAMA_MODEL,
            messages=[{'role': 'user', 'content': user_message}]
        )
        print(f"Ollama response: {response['message']['content']}")
        return response['message']['content']
    except Exception as e:
        print(f"Error communicating with Ollama: {e}")
        # Check if it's a connection error specifically
        if "Temporary failure in name resolution" in str(e) or "Connection refused" in str(e):
            return f"Ollama service at {ollama_host} is not reachable. Please ensure it's running and accessible."
        elif "model" in str(e).lower() and "not found" in str(e).lower():
             return f"Ollama model '{OLLAMA_MODEL}' not found. Please ensure it's pulled/available on the Ollama server."
        return f"Error getting response from Ollama: {str(e)}"

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')

@socketio.on('message')
def handle_message(data):
    user_id = request.sid
    print(f'Received message from {user_id}: {data}')

    # Emit the user's original message to all clients (including sender for their own history)
    # We'll let the client decide how to display "You" vs "Other" based on session or message structure
    emit('message', {'user': user_id, 'text': data, 'type': 'user_message'}, broadcast=True)
    print(f'Broadcasting user message to all clients: {data}')

    # Get Ollama response
    ollama_reply = get_ollama_response(data)

    if ollama_reply:
        print(f'Ollama responded: {ollama_reply}')
        # Broadcast Ollama's response to all clients
        emit('message', {'user': 'LLM', 'text': ollama_reply, 'type': 'llm_response'}, broadcast=True)
        print(f'Broadcasting LLM response to all clients: {ollama_reply}')
    else:
        # Optionally, inform the user that the LLM response failed
        emit('message', {'user': 'System', 'text': 'LLM is currently unavailable or encountered an error.', 'type': 'system_error'}, room=user_id)
        print('Ollama response was empty or an error occurred, not broadcasting LLM response.')

if __name__ == '__main__':
    print(f"Starting SocketIO server with Ollama host: {ollama_host} and model: {OLLAMA_MODEL}")
    socketio.run(app, host='0.0.0.0', port=5000)
