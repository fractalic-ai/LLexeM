#!/bin/bash

# Get the directory of the script (relative path resolution)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
SERVER_DIR="$SCRIPT_DIR/fractalic/ui_server"

# Activate virtual environment
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
else
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Navigate to server directory
cd "$SERVER_DIR" || { echo "Error: Failed to enter $SERVER_DIR"; exit 1; }

# Run Uvicorn server (fixing module import issue)
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
