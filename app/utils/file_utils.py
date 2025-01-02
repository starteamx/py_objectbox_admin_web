import os
import shutil
import subprocess
from datetime import datetime, timedelta
from app.config import OBJECTBOX_DIR, FILE_EXPIRE_MINUTES

def cleanup_old_files():
    """清理超过指定时间的文件和目录"""
    if not os.path.exists(OBJECTBOX_DIR):
        return
    
    current_time = datetime.now()
    for item in os.listdir(OBJECTBOX_DIR):
        item_path = os.path.join(OBJECTBOX_DIR, item)
        if item in ["objectbox-admin.sh", "nginx"]:
            continue
        
        modified_time = datetime.fromtimestamp(os.path.getmtime(item_path))
        if current_time - modified_time > timedelta(minutes=FILE_EXPIRE_MINUTES):
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            except Exception as e:
                print(f"清理文件失败: {item_path}, 错误: {str(e)}")

def stop_existing_container():
    """停止并清理所有 ObjectBox Admin 和 Nginx 实例容器"""
    try:
        # 1. 获取所有 objectbox-admin 容器
        admin_containers = subprocess.run(
            ["docker", "ps", "-aq", "--filter", "name=objectbox-admin-"],
            capture_output=True, text=True, check=True
        ).stdout.strip().split('\n')

        # 2. 获取所有 nginx 容器
        nginx_containers = subprocess.run(
            ["docker", "ps", "-aq", "--filter", "name=objectbox-nginx-"],
            capture_output=True, text=True, check=True
        ).stdout.strip().split('\n')

        # 3. 停止并删除容器
        for container_id in admin_containers + nginx_containers:
            if container_id:  # 确保容器ID不为空
                try:
                    # 停止容器
                    subprocess.run(
                        ["docker", "stop", container_id],
                        capture_output=True, check=True
                    )
                    # 删除容器
                    subprocess.run(
                        ["docker", "rm", container_id],
                        capture_output=True, check=True
                    )
                except subprocess.CalledProcessError as e:
                    print(f"清理容器 {container_id} 失败: {str(e)}")

        # 4. 清理未使用的网络
        networks = subprocess.run(
            ["docker", "network", "ls", "--filter", "name=objectbox-network-", "-q"],
            capture_output=True, text=True, check=True
        ).stdout.strip().split('\n')

        for network_id in networks:
            if network_id:
                try:
                    subprocess.run(
                        ["docker", "network", "rm", network_id],
                        capture_output=True, check=True
                    )
                except subprocess.CalledProcessError as e:
                    print(f"清理网络 {network_id} 失败: {str(e)}")

        print("已清理所有 ObjectBox Admin 和 Nginx 容器及网络")
        
    except Exception as e:
        print(f"清理容器和网络失败: {str(e)}") 