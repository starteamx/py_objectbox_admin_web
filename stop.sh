#!/bin/bash

APP_NAME="objectbox-admin"
PID_DIR="./run"
PID_FILE="$PID_DIR/${APP_NAME}.pid"

if [ -f "$PID_FILE" ]; then
    pid=$(cat "$PID_FILE")
    if ps -p "$pid" > /dev/null 2>&1; then
        echo "Stopping application (PID: $pid)..."
        kill "$pid"
        rm "$PID_FILE"
        echo "Application stopped"
    else
        echo "Application not running (stale PID file)"
        rm "$PID_FILE"
    fi
else
    echo "PID file not found"
fi 