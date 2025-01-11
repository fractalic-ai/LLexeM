#!/bin/bash

# Get the directory of the script (relative path resolution)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
SERVER_MODULE="llexem.ui_server.server:app"  # Module path for uvicorn

# Activate virtual environment
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
else
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Run Uvicorn server without changing directories
uvicorn "$SERVER_MODULE" --host 0.0.0.0 --port 8000 --reload
