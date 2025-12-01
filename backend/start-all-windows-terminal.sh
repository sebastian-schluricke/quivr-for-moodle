#!/bin/bash
# Start all services in separate Windows Terminal tabs
# This script launches Windows Terminal with multiple tabs

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Convert WSL path to Windows path
WIN_PATH=$(wslpath -w "$SCRIPT_DIR")

echo "Starting all Quivr services in Windows Terminal..."

# Start Windows Terminal with multiple tabs
# Note: This requires Windows Terminal to be installed
wt.exe \
    new-tab --title "Backend API" wsl.exe bash "$SCRIPT_DIR/start-backend.sh" `; \
    new-tab --title "Celery Worker" wsl.exe bash "$SCRIPT_DIR/start-celery.sh" `; \
    new-tab --title "Notifier" wsl.exe bash "$SCRIPT_DIR/start-notifier.sh"

echo "Windows Terminal launched with 3 tabs"
