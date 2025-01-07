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
        # 遍历实例ID 1-5
        for instance_id in range(1, 6):
            try:
                stop_instance_container(instance_id)
            except Exception as e:
                print(f"清理实例 {instance_id} 时发生错误: {str(e)}")
                continue  # 继续清理下一个实例
                
        print("已清理所有实例")
        
    except Exception as e:
        print(f"清理容器和网络失败: {str(e)}")

def stop_instance_container(instance_id: int):
    """停止并清理指定实例ID的 ObjectBox Admin 和 Nginx 容器"""
    try:
        # 1. 获取指定实例的 objectbox-admin 容器
        admin_container = subprocess.run(
            ["docker", "ps", "-aq", "--filter", f"name=objectbox-admin-{instance_id}"],
            capture_output=True, text=True, check=True
        ).stdout.strip()

        # 2. 获取指定实例的 nginx 容器
        nginx_container = subprocess.run(
            ["docker", "ps", "-aq", "--filter", f"name=nginx-proxy-{instance_id}"],
            capture_output=True, text=True, check=True
        ).stdout.strip()

        # 3. 停止并删除容器
        for container_id in [admin_container, nginx_container]:
            if container_id:  # 确保容器ID不为空
                try:
                    # 停止容器
                    subprocess.run(
                        ["docker", "stop", container_id],
                        capture_output=True, check=True
                    )
                    print(f"已停止容器: {container_id}")
                    
                    # 删除容器
                    subprocess.run(
                        ["docker", "rm", container_id],
                        capture_output=True, check=True
                    )
                    print(f"已删除容器: {container_id}")
                except subprocess.CalledProcessError as e:
                    print(f"清理容器 {container_id} 失败: {str(e)}")

        # 4. 清理网络
        network_id = subprocess.run(
            ["docker", "network", "ls", "--filter", f"name=objectbox-network-{instance_id}", "-q"],
            capture_output=True, text=True, check=True
        ).stdout.strip()

        if network_id:
            try:
                subprocess.run(
                    ["docker", "network", "rm", network_id],
                    capture_output=True, check=True
                )
                print(f"已删除网络: objectbox-network-{instance_id}")
            except subprocess.CalledProcessError as e:
                print(f"清理网络失败: {str(e)}")

        print(f"实例 {instance_id} 的所有资源已清理完成")
        
    except Exception as e:
        print(f"清理实例 {instance_id} 失败: {str(e)}") 