#!/bin/bash
# Start script for Quivr backend stack (without reload/watchdog)

cd "$(dirname "$0")"

# Kill any existing processes on our ports
echo "Cleaning up existing processes..."
pkill -f "uvicorn quivr_api.main:app" 2>/dev/null || true
pkill -f "celery -A quivr_worker" 2>/dev/null || true
pkill -f "python.*notifier" 2>/dev/null || true
sleep 2

# Activate venv
source api/venv/bin/activate

# Export environment variables from root .env
if [ -f ../.env ]; then
    echo "Loading environment from ../.env"
    export $(grep -v '^#' ../.env | xargs)
elif [ -f .env ]; then
    echo "Loading environment from .env"
    export $(grep -v '^#' .env | xargs)
fi

echo "========================================"
echo "Starting Quivr Backend Stack"
echo "========================================"

# Start Uvicorn (API) - no reload
echo "[1/3] Starting Uvicorn API server on port 5050..."
cd api
python -m uvicorn quivr_api.main:app --host 0.0.0.0 --port 5050 --log-level info &
UVICORN_PID=$!
cd ..

# Start Celery Worker
echo "[2/3] Starting Celery worker..."
cd worker
celery -A quivr_worker.celery_worker worker --loglevel=info &
CELERY_PID=$!
cd ..

# Start Notifier (Celery Monitor)
echo "[3/3] Starting Notifier (Celery Monitor)..."
cd worker
python -m quivr_worker.celery_monitor &
NOTIFIER_PID=$!
cd ..

echo "========================================"
echo "Stack started!"
echo "  Uvicorn PID: $UVICORN_PID"
echo "  Celery PID:  $CELERY_PID"
[ -n "$NOTIFIER_PID" ] && echo "  Notifier PID: $NOTIFIER_PID"
echo "========================================"
echo ""
echo "Waiting for API to be ready (this takes ~60s)..."
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for API to be ready
for i in {1..120}; do
    if curl -s http://localhost:5050/healthz > /dev/null 2>&1; then
        echo ""
        echo "API is ready! http://localhost:5050"
        break
    fi
    echo -n "."
    sleep 1
done

# Keep script running and handle Ctrl+C
trap "echo 'Stopping all services...'; kill $UVICORN_PID $CELERY_PID $NOTIFIER_PID 2>/dev/null; exit 0" SIGINT SIGTERM

wait
