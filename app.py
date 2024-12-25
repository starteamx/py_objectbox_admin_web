import os
import shutil
import uuid
import socket
import subprocess
import time
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.database.models import init_db
from app.database.manager import DatabaseManager

# 配置常量
OBJECTBOX_DIR = "objectbox"
ADMIN_PORT = 8081
FILE_EXPIRE_MINUTES = 1

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用的生命周期管理"""
    # 启动时执行
    init_db()  # 初始化数据库
    cleanup_old_files()
    stop_existing_container()
    
    # 确保 objectbox 目录存在
    os.makedirs(OBJECTBOX_DIR, exist_ok=True)
    
    yield  # 应用运行
    
    # 关闭时执行
    cleanup_old_files()
    stop_existing_container()

app = FastAPI(lifespan=lifespan)

# 配置模板和静态文件
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "localhost"

def cleanup_old_files():
    """清理超过指定时间的文件和目录"""
    if not os.path.exists(OBJECTBOX_DIR):
        return
    
    current_time = datetime.now()
    for item in os.listdir(OBJECTBOX_DIR):
        item_path = os.path.join(OBJECTBOX_DIR, item)
        # 过 objectbox-admin.sh 和 nginx 目录
        if item in ["objectbox-admin.sh", "nginx","t"]:
            continue
        
        # 检查文件/目录的修改时间
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
    """停止现有的 ObjectBox Admin Docker 容器"""
    try:
        # 查找并停止 objectbox-admin 容器
        subprocess.run(
            ["docker", "ps", "-q", "--filter", "ancestor=objectboxio/admin"],
            capture_output=True, text=True, check=True
        )
        
        # 停止所有 objectboxio/admin 镜像的容器
        subprocess.run(
            ["docker", "stop", "$(docker ps -q --filter ancestor=objectboxio/admin)"],
            shell=True,  # 使用 shell 执行命令
            capture_output=True
        )
        
        # 删除停止的容器
        subprocess.run(
            ["docker", "rm", "$(docker ps -aq --filter ancestor=objectboxio/admin)"],
            shell=True,  # 使用 shell 执行命令
            capture_output=True
        )
        
        print("已停止并删除现有的 ObjectBox Admin 容器")
    except Exception as e:
        print(f"停止 Docker 容器失败: {str(e)}")

@app.get("/")
async def home(request: Request):
    db_manager = DatabaseManager()
    instances = db_manager.get_all_instances()
    local_ip = get_local_ip()
    
    # 处理实例数据以适应模板
    instances_data = []
    for instance in instances:
        instance_dict = {
            "id": instance.id,
            "port": 8080 + instance.id,  # 外部访问端口
            "status": instance.status,
            "running_time": None,
            "time_percentage": 0
        }
        
        if instance.status == 'RUNNING' and instance.start_time:
            # 计算运行时间
            running_time = datetime.now() - instance.start_time
            minutes = running_time.seconds // 60
            seconds = running_time.seconds % 60
            instance_dict["running_time"] = f"{minutes}分钟{seconds}秒"
            instance_dict["time_percentage"] = min((running_time.seconds / 1800) * 100, 100)  # 30分钟为100%
        
        instances_data.append(instance_dict)
    
    return templates.TemplateResponse(
        "instance_status.html",
        {
            "request": request, 
            "instances": instances_data,
            "local_ip": local_ip
        }
    )

@app.get("/instance/{instance_id}")
async def instance_detail(request: Request, instance_id: int):
    db_manager = DatabaseManager()
    instance = db_manager.get_instance(instance_id)
    
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    if instance.status == 'RUNNING':
        raise HTTPException(status_code=400, detail="Instance is already running")
    
    return templates.TemplateResponse(
        "instance_upload.html",
        {
            "request": request,
            "instance": {
                "id": instance.id,
                "port": instance.port,
                "status": instance.status
            },
            "title": f"Instance #{instance_id}"
        }
    )

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    instance_id: int = Form(...)
):
    """处理文件上传并启动实例"""
    # 验证文件类型
    if not file.filename.endswith('.mdb'):
        raise HTTPException(status_code=400, detail="只接受 .mdb 文件")
    
    try:
        # 获取数据库管理器
        db_manager = DatabaseManager()
        instance = db_manager.get_instance(instance_id)
        
        if not instance or instance.status == 'RUNNING':
            raise HTTPException(status_code=400, detail="实例不可用")

        # 使用项目根目录
        root_dir = os.path.dirname(os.path.abspath(__file__))
        instance_dir = os.path.join(root_dir, "objectbox", f"instance_{instance_id}")
        db_dir = os.path.join(instance_dir, "objectbox")
        
        # 确保目录存在
        os.makedirs(db_dir, exist_ok=True)
        
        # 保存上传的文件
        file_path = os.path.join(db_dir, "data.mdb")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 设置端口
        nginx_port = 8080 + instance_id
        
        # 启动服务（使用项目根目录）
        process = subprocess.Popen(
            [
                "./objectbox/objectbox-admin.sh",
                "--instance-id", str(instance_id),
                "--nginx-port", str(nginx_port),
                "--db-path", db_dir
            ],
            cwd=root_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 更新实例状态
        db_manager.update_instance_status(
            instance_id, 
            'RUNNING', 
            str(process.pid)
        )
        
        # 记录活动日志
        db_manager.log_activity(
            instance_id,
            None,
            None,
            "START",
            f"Started with file: {file.filename}"
        )
        time.sleep(5)
        # 返回访问URL
        local_ip = get_local_ip()
        return {
            "status": "success",
            "url": f"http://{local_ip}:{nginx_port}",
            "instance_id": instance_id
        }

    except Exception as e:
        # 记录错误
        logger.error(f"实例 {instance_id} 启动失败: {str(e)}")
        # 清理资源
        if 'process' in locals():
            process.kill()
        # 更新状态
        if 'db_manager' in locals():
            db_manager.update_instance_status(instance_id, 'ERROR')
        
        raise HTTPException(
            status_code=500,
            detail=f"启动实例失败: {str(e)}"
        )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 