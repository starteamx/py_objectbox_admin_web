#!/bin/sh

# ObjectBox Admin shell script for Docker container version.
# For more information visit https://objectbox.io

usage() {
    [ $# -eq 0 ] || echo "$1" 1>&2
    cat <<EOF 1>&2
usage: $0 [options] 

Available options:
  --instance-id <id>        Instance ID (required)
  --nginx-port <port>       External nginx port (default: 8080+instance_id)
  --db-path <path>         Database directory path (required)

Example:
  $0 --instance-id 1 --db-path /data/instance_1/objectbox
EOF
    exit 1
}

# 默认值
INSTANCE_ID=""
DB_PATH=""
NGINX_PORT=""

# 参数解析
while [ $# -gt 0 ]; do
    case "$1" in
        --instance-id)
            [ $# -ge 2 ] || usage "Missing instance ID"
            INSTANCE_ID="$2"
            shift 2
            ;;
        --nginx-port)
            [ $# -ge 2 ] || usage "Missing nginx port"
            NGINX_PORT="$2"
            shift 2
            ;;
        --db-path)
            [ $# -ge 2 ] || usage "Missing database path"
            DB_PATH="$2"
            shift 2
            ;;
        --help|-h)
            usage
            ;;
        *)
            usage "Unknown option: $1"
            ;;
    esac
done

# 验证必需参数
[ -n "$INSTANCE_ID" ] || usage "Instance ID is required"
[ -n "$DB_PATH" ] || usage "Database path is required"
[ -n "$NGINX_PORT" ] || NGINX_PORT=$((8080 + INSTANCE_ID))

# 设置网络名称
NETWORK_NAME="objectbox-network-${INSTANCE_ID}"

# 设置容器名称
ADMIN_CONTAINER="objectbox-admin-${INSTANCE_ID}"
NGINX_CONTAINER="nginx-proxy-${INSTANCE_ID}"

# 设置配置目录（使用项目根目录的绝对路径）
ROOT_DIR="$(pwd)"
INSTANCE_DIR="${ROOT_DIR}/objectbox/instance_${INSTANCE_ID}"
NGINX_CONF_DIR="${INSTANCE_DIR}/nginx/conf.d"
TEMPLATE_CONF="${ROOT_DIR}/nginx/conf.d/template.conf"

echo "Starting ObjectBox Admin with configuration:"
echo "- Instance ID: ${INSTANCE_ID}"
echo "- Nginx Port: ${NGINX_PORT}"
echo "- Instance Directory: ${INSTANCE_DIR}"
echo "- Nginx Config Dir: ${NGINX_CONF_DIR}"
echo "- Template Config: ${TEMPLATE_CONF}"
echo "- Network: ${NETWORK_NAME}"
echo "=================================================================="

# 创建网络（如果不存在）
if ! docker network inspect "${NETWORK_NAME}" >/dev/null 2>&1; then
    echo "Creating network ${NETWORK_NAME}..."
    docker network create "${NETWORK_NAME}" || exit 1
fi

# 清理同ID的旧容器
echo "Cleaning up old containers..."
docker rm -f "${ADMIN_CONTAINER}" "${NGINX_CONTAINER}" 2>/dev/null || true

# 准备 Nginx 配置目录
mkdir -p "${NGINX_CONF_DIR}"

# 从模板生成 Nginx 配置
echo "Generating Nginx configuration..."
sed "s/\${INSTANCE_ID}/${INSTANCE_ID}/g" "${TEMPLATE_CONF}" > "${NGINX_CONF_DIR}/default.conf"

# 启动 ObjectBox Admin 容器
echo "Starting ObjectBox Admin container..."
if ! docker run -d \
    --name "${ADMIN_CONTAINER}" \
    --network "${NETWORK_NAME}" \
    -v "${DB_PATH}:/db:rw" \
    objectboxio/admin:latest; then
    echo "Failed to start Admin container"
    exit 1
fi

# 检查 Admin 容器是否成功启动
if ! docker ps | grep -q "${ADMIN_CONTAINER}"; then
    echo "Admin container failed to start. Checking logs..."
    docker logs "${ADMIN_CONTAINER}"
    exit 1
fi

echo "ObjectBox Admin container started successfully"

# 启动 Nginx 容器
echo "Starting Nginx container..."
if ! docker run -d \
    --name "${NGINX_CONTAINER}" \
    --network "${NETWORK_NAME}" \
    -p "${NGINX_PORT}:80" \
    -v "${NGINX_CONF_DIR}:/etc/nginx/conf.d:ro" \
    nginx:alpine; then
    echo "Failed to start Nginx container"
    docker rm -f "${ADMIN_CONTAINER}"
    exit 1
fi

# 检查服务状态
echo "Checking service status..."
sleep 2

if docker ps | grep -q "${ADMIN_CONTAINER}" && \
   docker ps | grep -q "${NGINX_CONTAINER}"; then
    echo "Service started successfully"
    echo "Access via: http://localhost:${NGINX_PORT}"
else
    echo "Service failed to start"
    docker logs "${ADMIN_CONTAINER}"
    docker logs "${NGINX_CONTAINER}"
    docker rm -f "${ADMIN_CONTAINER}" "${NGINX_CONTAINER}"
    exit 1
fi

# 设置清理钩子
cleanup() {
    echo "Stopping containers..."
    docker stop "${ADMIN_CONTAINER}" "${NGINX_CONTAINER}"
    echo "Service stopped"
}

trap cleanup INT TERM

# 等待中断信号
echo "Service is running. Press Ctrl+C to stop."
while true; do sleep 1; done