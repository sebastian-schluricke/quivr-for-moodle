#!/bin/bash
# Stop all Quivr services or kill tmux session

SESSION_NAME="quivr-dev"

echo "Stopping Quivr services..."

# Check if tmux session exists
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "Killing tmux session: $SESSION_NAME"
    tmux kill-session -t $SESSION_NAME
    echo "✓ Tmux session killed"
else
    echo "No tmux session found. Stopping individual processes..."

    # Stop backend
    echo "  Stopping backend..."
    pkill -f "uvicorn quivr_api.main:app" 2>/dev/null && echo "  ✓ Backend stopped" || echo "  ℹ  No backend process found"

    # Stop frontend
    echo "  Stopping frontend..."
    lsof -t -i:3000 | xargs kill -9 2>/dev/null && echo "  ✓ Frontend stopped" || echo "  ℹ  No frontend process found"
    pkill -f "npm.*dev" 2>/dev/null || true

    # Stop celery
    echo "  Stopping celery..."
    pkill -f "celery.*worker" 2>/dev/null && echo "  ✓ Celery stopped" || echo "  ℹ  No celery process found"

    # Stop notifier
    echo "  Stopping notifier..."
    pkill -f "celery_monitor" 2>/dev/null && echo "  ✓ Notifier stopped" || echo "  ℹ  No notifier process found"
fi

echo ""
echo "✅ All services stopped"
echo ""
echo "Note: Supabase is still running. To stop it:"
echo "  cd backend && supabase stop"

