#!/bin/bash
# Restart all services in existing tmux session

SESSION_NAME="quivr-dev"

# Check if session exists
if ! tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "Error: Session $SESSION_NAME not found!"
    echo "Start services first with: ./start-all.sh"
    exit 1
fi

echo "Restarting all services in session: $SESSION_NAME"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Kill all processes in all panes (send Ctrl+C)
tmux send-keys -t $SESSION_NAME:0.0 C-c
tmux send-keys -t $SESSION_NAME:0.1 C-c
tmux send-keys -t $SESSION_NAME:0.2 C-c
tmux send-keys -t $SESSION_NAME:0.3 C-c 2>/dev/null || true

# Wait a moment for processes to stop
sleep 3

# Restart backend in pane 0
tmux send-keys -t $SESSION_NAME:0.0 "cd '$SCRIPT_DIR' && bash start-backend.sh" Enter

# Restart celery in pane 1
tmux send-keys -t $SESSION_NAME:0.1 "cd '$SCRIPT_DIR' && bash start-celery.sh" Enter

# Restart notifier in pane 2
tmux send-keys -t $SESSION_NAME:0.2 "cd '$SCRIPT_DIR' && bash start-notifier.sh" Enter

# Restart frontend in pane 3 (if it exists)
tmux send-keys -t $SESSION_NAME:0.3 "cd '$SCRIPT_DIR' && bash start-frontend.sh" Enter 2>/dev/null || true

echo "All services restarted!"
echo "To view: tmux attach -t $SESSION_NAME"
