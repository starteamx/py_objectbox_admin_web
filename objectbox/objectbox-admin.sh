#!/bin/sh

# ObjectBox Admin front-end shell script for Docker container version.
# For more information visit https://objectbox.io
# Detailed documentation available at https://docs.objectbox.io/data-browser 

usage()
{
    [ $# -eq 0 ] || echo "$1" 1>&2  
    cat <<EOF 1>&2 

usage: $0 [options] [<database-directory>]

<database-directory> ( defaults to ./objectbox ) should contain an objectbox "data.mdb" file.

Available (optional) options:
  [--port <port-number>] Mapped bind port to localhost (defaults to 8081)
 
EOF
    exit 1
}

port=8081

while [ $# -ne 0 ]; do
    case $1 in
        --help|-h)
            usage
            ;;
        --port)
            [ $# -ge 2 ] || usage
            port=$2
            shift 2
            ;;
        -*|--*)
            usage
            ;;
        *) 
            break
            ;;
    esac
done

[ $# -le 1 ] || usage

db=${1:-.}

echo "Objectbox Admin (Docker-Version)"
echo ""

if [ ! -f "$db/data.mdb" ]; then
    echo "NOTE: No database found at location '$db', trying default location ('$db/objectbox') .." 
    db=$db/objectbox
fi 

[ -f "$db/data.mdb" ] || usage "Oops.. no database file found at '$db/data.mdb'. Please check the path to the database directory."

# make db an absolute path and resolve symbolic links
db=$( cd "$db" ; pwd -P )

echo "Found database at local location '${db}'."
echo "Starting container with the following configuration:"
echo "- Database path: ${db}"
echo "- Port: ${port}"
echo "- Network mode: host"
echo "=================================================================="

# 确保网络存在
docker network create objectbox-network 2>/dev/null || true

# 清理旧容器（如果存在）
docker rm -f objectbox-admin nginx-proxy 2>/dev/null || true

# 启动 ObjectBox Admin 容器（使用固定容器名）
docker run -d \
    --name objectbox-admin \
    --network objectbox-network \
    -v "$db:/db" \
    -u $(id -u):$(id -g) \
    objectboxio/admin:latest

# 启动 Nginx 代理（使用固定容器名）
docker run -d \
    --name nginx-proxy \
    --network objectbox-network \
    -p ${port}:8081 \
    -v $(pwd)/nginx/conf.d:/etc/nginx/conf.d:ro \
    nginx:alpine

echo "Checking container status..."

# 等待容器启动
sleep 2

# 检查容器状态
if docker ps | grep -q objectbox-admin && docker ps | grep -q nginx-proxy; then
    echo "Containers are running"
    echo "ObjectBox Admin logs:"
    docker logs objectbox-admin
    echo "Nginx logs:"
    docker logs nginx-proxy
else
    echo "Containers failed to start"
    echo "ObjectBox Admin logs:"
    docker logs objectbox-admin
    echo "Nginx logs:"
    docker logs nginx-proxy
    exit 1
fi

echo "Open http://127.0.0.1:${port} or http://$(hostname -I | awk '{print $1}'):${port} in a browser."
echo "Once done, hit CTRL+C to stop containers."
echo "=================================================================="

# 等待用户输入并清理所有容器
trap "docker stop objectbox-admin nginx-proxy && docker rm objectbox-admin nginx-proxy" INT
while true; do sleep 1; done
