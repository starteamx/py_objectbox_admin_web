#!/bin/bash

# 应用配置
APP_NAME="objectbox-admin"
APP_PORT=8000
VENV_DIR="./venv"
PID_DIR="./run"
LOG_DIR="./logs"
PID_FILE="$PID_DIR/${APP_NAME}.pid"
LOG_FILE="$LOG_DIR/${APP_NAME}.log"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查系统环境
check_environment() {
    echo -e "${YELLOW}Checking environment...${NC}"
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python3 is not installed. Please install Python3 first.${NC}"
        exit 1
    fi
    
    # 检查 pip
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}pip3 is not installed. Please install pip3 first.${NC}"
        exit 1
    fi
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
        exit 1
    fi
}

# 创建并激活虚拟环境
setup_virtualenv() {
    echo -e "${YELLOW}Setting up virtual environment...${NC}"
    
    # 如果虚拟环境不存在，创建它
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        echo -e "${GREEN}Virtual environment created.${NC}"
    fi
    
    # 激活虚拟环境
    source "$VENV_DIR/bin/activate"
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        echo -e "${YELLOW}Installing dependencies...${NC}"
        pip install -r requirements.txt
        echo -e "${GREEN}Dependencies installed.${NC}"
    fi
}

# 创建必要的目录
create_directories() {
    echo -e "${YELLOW}Creating necessary directories...${NC}"
    mkdir -p "$PID_DIR" "$LOG_DIR"
    chmod -R 755 "$PID_DIR" "$LOG_DIR"
}

# 检查应用状态
check_app_status() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${RED}Application is already running with PID: $pid${NC}"
            exit 1
        else
            echo -e "${YELLOW}Removing stale PID file${NC}"
            rm "$PID_FILE"
        fi
    fi
}

# 启动应用
start_application() {
    echo -e "${YELLOW}Starting application...${NC}"
    
    # 启动应用
    nohup uvicorn app:app --host 0.0.0.0 --port $APP_PORT > "$LOG_FILE" 2>&1 & 
    new_pid=$!
    
    # 等待几秒检查应用是否成功启动
    sleep 3
    if ps -p $new_pid > /dev/null 2>&1; then
        echo $new_pid > "$PID_FILE"
        echo -e "${GREEN}Application started successfully!${NC}"
        echo -e "${GREEN}PID: $new_pid${NC}"
        echo -e "${GREEN}Port: $APP_PORT${NC}"
        echo -e "${GREEN}Log file: $LOG_FILE${NC}"
    else
        echo -e "${RED}Failed to start application. Check logs for details.${NC}"
        exit 1
    fi
}

# 显示使用信息
show_usage() {
    echo -e "\n${GREEN}Application is running!${NC}"
    echo -e "\n${YELLOW}Usage:${NC}"
    echo -e "  Stop application: ${GREEN}./stop.sh${NC}"
    echo -e "  View logs: ${GREEN}tail -f $LOG_FILE${NC}"
    echo -e "  Access application: ${GREEN}http://localhost:$APP_PORT${NC}"
}

# 主函数
main() {
    echo -e "${GREEN}Deploying $APP_NAME...${NC}"
    
    check_environment
    setup_virtualenv
    create_directories
    check_app_status
    start_application
    show_usage
}

# 执行主函数
main 