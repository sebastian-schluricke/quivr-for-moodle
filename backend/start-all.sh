#!/bin/bash
# Start all services in separate tmux panes

SESSION_NAME="quivr-dev"

# Check if tmux session already exists
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "Session $SESSION_NAME already exists. Attaching..."
    tmux attach-session -t $SESSION_NAME
    exit 0
fi

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Starting all Quivr services in tmux session: $SESSION_NAME"
echo ""
echo "Pane Layout:"
echo "  Pane 0 (left):       Backend API (port 5050) - auto-reload"
echo "  Pane 1 (top-right):  Celery Worker - watchdog auto-restart"
echo "  Pane 2 (mid-right):  Notifier"
echo "  Pane 3 (bot-right):  Frontend (port 3000)"
echo ""
echo "Tmux Commands:"
echo "  Ctrl+b then d     - Detach from session (services keep running)"
echo "  Ctrl+b then arrow - Navigate between panes"
echo "  Ctrl+b then x     - Kill current pane"
echo "  Ctrl+c            - Stop service in current pane"
echo ""
echo "To reattach later: tmux attach -t $SESSION_NAME"
echo "To kill session:   tmux kill-session -t $SESSION_NAME"
echo ""
read -p "Press Enter to start..."

# Create new tmux session with first pane running backend
tmux new-session -d -s $SESSION_NAME -n 'quivr' "cd '$SCRIPT_DIR' && bash start-backend.sh; bash"

# Split window horizontally and start celery
tmux split-window -h -t $SESSION_NAME "cd '$SCRIPT_DIR' && bash start-celery.sh; bash"

# Split the right pane vertically and start notifier
tmux split-window -v -t $SESSION_NAME "cd '$SCRIPT_DIR' && bash start-notifier.sh; bash"

# Split the right pane vertically again and start frontend
tmux split-window -v -t $SESSION_NAME "cd '$SCRIPT_DIR' && bash start-frontend.sh; bash"

# Select the layout
tmux select-layout -t $SESSION_NAME main-vertical

# Attach to the session
tmux attach-session -t $SESSION_NAME
