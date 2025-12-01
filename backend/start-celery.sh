#!/bin/bash
# Start Celery Worker with watchdog auto-reload

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/worker"

echo "Starting Celery Worker..."

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

# Check if watchdog/watchmedo is available
if command -v watchmedo &> /dev/null; then
    echo "Starting Celery Worker with watchdog auto-reload..."
    echo "Watching: $SCRIPT_DIR/worker and $SCRIPT_DIR/api for changes"
    watchmedo auto-restart \
        --directory="$SCRIPT_DIR/worker" \
        --directory="$SCRIPT_DIR/api" \
        --pattern="*.py" \
        --recursive \
        -- python -m celery -A quivr_worker.celery_worker worker -l info -E
else
    echo "Warning: watchmedo not found, starting without auto-reload"
    echo "Install with: pip install watchdog"
    python -m celery -A quivr_worker.celery_worker worker -l info -E
fi
