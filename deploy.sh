#!/bin/bash

APP_NAME="objectbox-admin"
PID_DIR="./run"
PID_FILE="$PID_DIR/${APP_NAME}.pid"
LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/${APP_NAME}.log"

# 创建必要的目录
mkdir -p "$PID_DIR" "$LOG_DIR"

# 检查是否已经运行
if [ -f "$PID_FILE" ]; then
    pid=$(cat "$PID_FILE")
    if ps -p "$pid" > /dev/null 2>&1; then
        echo "Application is already running with PID: $pid"
        exit 1
    else
        echo "Removing stale PID file"
        rm "$PID_FILE"
    fi
fi

# 启动应用
nohup uvicorn app:app --host 0.0.0.0 --port 8000 > "$LOG_FILE" 2>&1 & 
new_pid=$!

# 保存 PID
echo $new_pid > "$PID_FILE"

echo "Application started with PID: $new_pid"
echo "PID file: $PID_FILE"
echo "Log file: $LOG_FILE"
echo ""
echo "To stop the application:"
echo "./stop.sh"
echo ""
echo "To view logs:"
echo "tail -f $LOG_FILE" 