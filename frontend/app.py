import streamlit as st
import socketio
import requests # Required for python-socketio[client]

# --- Page Configuration ---
st.set_page_config(page_title="Real-time Chat", layout="wide")

# --- Session State Initialization ---
if "sio" not in st.session_state:
    st.session_state.sio = socketio.Client(reconnection_attempts=3, logger=True, engineio_logger=True)
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "connection_status" not in st.session_state:
    st.session_state.connection_status = "Disconnected"
if "connected_once" not in st.session_state: # To prevent multiple connection attempts on rerun
    st.session_state.connected_once = False


# --- Socket.IO Client and Event Handlers ---
sio = st.session_state.sio

@sio.event
def connect():
    st.session_state.connection_status = "Connected"
    st.session_state.chat_messages.append({"user": "System", "text": "Connected to server."})
    st.rerun()

@sio.event
def connect_error(data):
    st.session_state.connection_status = f"Connection Failed: {data}"
    st.session_state.chat_messages.append({"user": "System", "text": f"Connection error: {data}"})
    st.rerun()

@sio.event
def disconnect():
    st.session_state.connection_status = "Disconnected"
    st.session_state.chat_messages.append({"user": "System", "text": "Disconnected from server."})
    st.session_state.connected_once = False # Allow reconnection attempt
    st.rerun()

@sio.on('message') # Default event name from server
def handle_message(data):
    # Data is now expected to be a dictionary, e.g., {'user': 'LLM', 'text': 'Hello', 'type': 'llm_response'}
    # or {'user': 'some_user_sid', 'text': 'Hi there', 'type': 'user_message'}

    user_display_name = "Other" # Default for messages from other users
    if isinstance(data, dict):
        message_text = data.get("text", "")
        message_type = data.get("type", "")
        sender_id = data.get("user", "") # SID or "LLM"

        if message_type == "llm_response":
            user_display_name = "LLM"
        elif message_type == "user_message":
            # If we want to distinguish "You" vs "Other" for user messages,
            # we'd need the client's own SID. For now, all non-LLM are "Other".
            # The backend sends user_id (sid), but client doesn't know its own sid by default with this lib.
            # A simple approach is to let the backend handle not sending user's own message back,
            # or the client identifies its own messages before sending.
            # Since the backend now sends all messages to all, we can just display them.
            # For now, we will rely on the fact that the user's own message is already added to chat_messages locally.
            # This handler is primarily for messages from *other* users or the LLM.
            if sender_id == st.session_state.sio.sid and message_type == 'user_message':
                # This is an echo of the user's own message from the server.
                # We already added it locally, so we can choose to ignore it here
                # or ensure our local adding logic handles potential duplicates if server echoes.
                # For simplicity, if we've added it locally, we might just return to avoid duplication.
                return # Assuming local message already added
            user_display_name = f"User ({sender_id[:5]})" if sender_id else "Other"

        elif message_type == "system_error":
            user_display_name = "System"

        st.session_state.chat_messages.append({"user": user_display_name, "text": message_text})
    else:
        # Fallback for simple string messages (old format)
        st.session_state.chat_messages.append({"user": "Other", "text": str(data)})
    st.rerun()

# --- Connection Management ---
# Use environment variable for backend URL, default for local testing
import os
backend_url = os.getenv("BACKEND_URL", "http://localhost:5000")

# Attempt to connect only if not already connected and haven't tried yet in this session
if not st.session_state.sio.connected and not st.session_state.connected_once :
    try:
        st.session_state.connection_status = "Connecting..."
        st.session_state.chat_messages.append({"user": "System", "text": f"Attempting to connect to {backend_url}..."})
        sio.connect(backend_url, wait_timeout=10) # Increased timeout
        st.session_state.connected_once = True # Mark that connection attempt has been made
    except socketio.exceptions.ConnectionError as e:
        st.session_state.connection_status = f"Connection Error: {e}"
        st.session_state.connected_once = True # Mark that connection attempt has been made
        st.session_state.chat_messages.append({"user": "System", "text": f"Could not connect to backend at {backend_url}. Error: {e}"})


# --- UI Display ---
st.title("Real-time Chat with Socket.IO")
st.write(f"Status: {st.session_state.connection_status}")

# Display chat messages
st.markdown("### Chat")
chat_container = st.container(height=400) # Explicit height for scrolling
with chat_container:
    for i, msg in enumerate(st.session_state.chat_messages):
        # Use a key to prevent issues with re-rendering identical messages
        chat_container.chat_message(name=msg["user"], key=f"msg_{i}").write(msg["text"])


# Chat input
prompt = st.chat_input("Say something")
if prompt:
    # Display user's message immediately with "You"
    st.session_state.chat_messages.append({"user": "You", "text": prompt})

    # Send message to server if connected
    if sio.connected:
        try:
            sio.emit('message', prompt) # Backend expects just the string
        except Exception as e:
            st.error(f"Error sending message: {e}")
            st.session_state.chat_messages.append({"user": "System", "text": f"Error sending: {e}"})
    else:
        st.warning("Not connected to server. Message not sent.")
        st.session_state.chat_messages.append({"user": "System", "text": "Message not sent (not connected)."})
    st.rerun()

# Add a disconnect button for testing
if st.button("Disconnect Manually"):
    if sio.connected:
        sio.disconnect()
    else:
        st.warning("Already disconnected.")

st.caption("Note: If the backend is not running, connection attempts will fail.")
