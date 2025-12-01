#!/bin/bash
# Start Backend API with auto-reload

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/api"

echo "Starting Backend API..."

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

# Check if venv exists
if [ -d "venv" ]; then
    echo "Activating venv..."
    source venv/bin/activate
else
    echo "Error: venv not found. Create it with: python3 -m venv venv"
    exit 1
fi

# WSL Detection: Force polling for file watching on mounted Windows drives
# inotify doesn't work reliably on /mnt/c/ paths
if [[ "$PWD" == /mnt/* ]]; then
    echo "WSL detected with mounted Windows drive - enabling polling mode for file watching"
    export WATCHFILES_FORCE_POLLING=1
fi

# Start backend with auto-reload using watchfiles (better WSL support)
echo "Starting uvicorn on http://localhost:5050"
python -m uvicorn quivr_api.main:app --host 0.0.0.0 --port 5050 --reload --log-level info
