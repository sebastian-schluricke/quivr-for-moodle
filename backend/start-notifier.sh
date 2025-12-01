#!/bin/bash
# Start Notifier Service (Celery Monitor)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/worker"

echo "Starting Notifier Service..."

# Load environment variables from root .env file
ENV_FILE="$SCRIPT_DIR/../.env"
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment from: $ENV_FILE"
    set -a
    source "$ENV_FILE"
    set +a
else
    echo "Warning: .env file not found at $ENV_FILE"
fi

# Check if venv exists in api directory (shared venv)
VENV_DIR="$SCRIPT_DIR/api/venv"
if [ -d "$VENV_DIR" ]; then
    echo "Activating venv from $VENV_DIR..."
    source "$VENV_DIR/bin/activate"
else
    echo "Error: venv not found at $VENV_DIR"
    exit 1
fi

# Start notifier
echo "Starting Notifier..."
python -m quivr_worker.celery_monitor
