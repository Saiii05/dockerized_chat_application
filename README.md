# Real-Time Dockerized Chat App with Local LLM (Ollama)

## Overview

This project is a real-time chat application that integrates a locally hosted Large Language Model (LLM) using Ollama. The application uses Socket.IO for real-time bidirectional communication between a Python Flask backend and a Streamlit frontend. The entire application stack (backend, frontend, and Ollama) is containerized using Docker and managed with Docker Compose for easy setup and deployment.

**Key Technologies:**
*   **Backend**: Python, Flask, Flask-SocketIO
*   **Frontend**: Python, Streamlit
*   **LLM**: Ollama (running models like Mistral, Llama3, etc.)
*   **Real-time Communication**: Socket.IO
*   **Containerization**: Docker, Docker Compose

## Features

*   **Real-time Messaging**: Instant message exchange between users.
*   **LLM Integration**: Chat with a local LLM; user messages are sent to the LLM, and responses are broadcast back to the chat.
*   **Multi-user Support**: Multiple users can join the chat and interact simultaneously.
*   **Fully Containerized**: Easy to set up and run with Docker, ensuring a consistent environment.

## Prerequisites

*   **Docker**: Docker Engine and Docker Compose (v2 or later) must be installed. Get Docker [here](https://www.docker.com/get-started).
*   **Internet Connection**: Required for pulling Docker images (Python, Ollama) and for the initial download of the LLM model into Ollama.
*   **(Optional) Git**: For cloning the repository.

## Setup and Running the Application

1.  **Clone the Repository** (if you haven't already):
    ```bash
    git clone https://github.com/Saiii05/dockerized_chat_application.git
    cd dockerized_chat_application
    ```

2.  **Build and Start the Services**:
    Navigate to the root directory of the project (where `docker-compose.yml` is located) and run:
    ```bash
    docker-compose up --build -d
    ```
    The `-d` flag runs the containers in detached mode.

3.  **Important: First-Time Ollama Model Setup**:
    After the containers are up and running for the first time (check with `docker-compose ps`), you need to pull an LLM model into the Ollama service. The default model expected by the backend is `mistral`.
    Open a new terminal and run:
    ```bash
    docker-compose exec ollama ollama pull mistral
    ```
    You can replace `mistral` with another model if you prefer (e.g., `llama3`, `codellama`). If you use a different model, you should update the `OLLAMA_MODEL` environment variable in the `backend` service definition within the `docker-compose.yml` file. After changing it, recreate the backend service:
    ```bash
    docker-compose up -d --force-recreate backend
    ```

4.  **Accessing the Frontend**:
    Once the services are running and the model is pulled, open your web browser and navigate to:
    [http://localhost:8501](http://localhost:8501)

## How to Use

*   Open the application in your browser.
*   The connection status to the backend server will be displayed.
*   Type your message in the chat input box at the bottom of the page and press Enter.
*   Your message will appear in the chat window, prefixed with "You:".
*   The message will also be sent to the Ollama LLM.
*   The LLM's response will appear in the chat, prefixed with "LLM:".
*   Other users connected to the application will see your messages and the LLM's responses in real-time.

## Project Structure

```
.
├── app/                    # Backend Flask-SocketIO application
│   ├── main.py             # Main Flask-SocketIO server logic
│   └── requirements.txt    # Python dependencies for the backend
├── frontend/               # Frontend Streamlit application
│   ├── app.py              # Main Streamlit UI and client logic
│   └── requirements.txt    # Python dependencies for the frontend
├── Dockerfile.backend      # Dockerfile for building the backend image
├── Dockerfile.frontend     # Dockerfile for building the frontend image
├── docker-compose.yml      # Docker Compose file to orchestrate all services
└── README.md               # This file
```

## Stopping the Application

To stop all running services, navigate to the project's root directory and run:
```bash
docker-compose down
```
This will stop and remove the containers. If you want to remove the named volume `ollama_data` (which stores the downloaded LLM models), you can run `docker-compose down -v`.

## Troubleshooting

*   **Ollama Service Issues**:
    *   If the `ollama` service fails to start or is unhealthy, check its logs:
        ```bash
        docker-compose logs ollama
        ```
    *   Ensure you have pulled a model after the first startup (see "First-Time Ollama Model Setup").
*   **Port Conflicts**:
    *   Ensure that ports `11434` (for Ollama), `5000` (for the backend), and `8501` (for the frontend) are not already in use by other applications on your host machine.
*   **Connection Issues (Frontend to Backend)**:
    *   Check the frontend logs: `docker-compose logs frontend`
    *   Check the backend logs: `docker-compose logs backend`
    *   Verify that the `BACKEND_URL` in `frontend/app.py` (derived from the environment variable in `docker-compose.yml`) correctly points to the backend service (`http://backend:5000`).
*   **LLM Model Not Found**:
    *   If the backend logs show errors like "model ... not found", ensure the model name specified in `OLLAMA_MODEL` (in `docker-compose.yml` for the `backend` service) matches the model you pulled into Ollama.
```
