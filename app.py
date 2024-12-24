import os
import shutil
import uuid
import socket
import subprocess
import time
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# 配置常量
OBJECTBOX_DIR = "objectbox"
ADMIN_PORT = 8081
FILE_EXPIRE_MINUTES = 1

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用的生命周期管理"""
    # 启动时执行
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
        if item in ["objectbox-admin.sh", "nginx"]:
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
    # 测试数据
    test_instances = [
        {
            "id": 1,
            "port": 8081,
            "status": "RUNNING",
            "running_time": "15分钟30秒",
            "time_percentage": 45
        },
        {
            "id": 2,
            "port": 8082,
            "status": "IDLE",
            "running_time": None,
            "time_percentage": 0
        },
        {
            "id": 3,
            "port": 8083,
            "status": "RUNNING",
            "running_time": "5m 12s",
            "time_percentage": 15
        },
        {
            "id": 4,
            "port": 8084,
            "status": "IDLE",
            "running_time": None,
            "time_percentage": 0
        },
        {
            "id": 5,
            "port": 8085,
            "status": "IDLE",
            "running_time": None,
            "time_percentage": 0
        }
    ]
    
    return templates.TemplateResponse(
        "instance_status.html", 
        {"request": request, "instances": test_instances}
    )

@app.get("/instance/{instance_id}")
async def instance_detail(request: Request, instance_id: int):
    # 检查实例状态
    # 这里应该检查实例是否处于空闲状态
    instance = {
        "id": instance_id,
        "port": 8080 + instance_id,
        "status": "IDLE",  # 只有空闲状态才能进入上传页面
        "running_time": None,
        "time_percentage": 0
    }
    
    return templates.TemplateResponse(
        "instance_upload.html",
        {
            "request": request, 
            "instance": instance,
            "title": f"Instance #{instance_id}"
        }
    )

@app.post("/upload")
async def upload_file(dbFile: UploadFile = File(..., alias="file")):
    """处理文件上传"""
    if not dbFile.filename.endswith('.mdb'):
        raise HTTPException(status_code=400, detail="只接受 .mdb 文件")

    # 清理旧文件和进程
    cleanup_old_files()
    stop_existing_container()

    # 创建唯一的目录名并使用绝对路径
    unique_dir = str(uuid.uuid4())
    base_dir = os.path.abspath(os.path.join(OBJECTBOX_DIR, unique_dir))
    db_dir = os.path.join(base_dir, "objectbox")  # 创建 objectbox 子目录

    print(f"创建目录结构:")
    print(f"base_dir: {base_dir}")
    print(f"db_dir: {db_dir}")

    # 文件操作部分使用单独的错误处理
    try:
        # 先创建基础目录
        os.makedirs(base_dir, exist_ok=True)
        print(f"基础目录创建成功: {base_dir}")
        
        # 再创建数据库目录
        os.makedirs(db_dir, exist_ok=True)
        print(f"数据库目录创建成功: {db_dir}")

        # 保存上传的文件到 objectbox 子目录
        file_path = os.path.join(db_dir, "data.mdb")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(dbFile.file, buffer)
        print(f"文件保存成功: {file_path}")
    except Exception as e:
        print(f"文件操作失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件操作失败: {str(e)}")

    # 启动 ObjectBox Admin
    admin_script = os.path.abspath(os.path.join(OBJECTBOX_DIR, "objectbox-admin.sh"))
    print(f"使用脚本: {admin_script}")
    print(f"工作目录: {os.path.dirname(admin_script)}")
    print(f"数据库目录: {base_dir}")

    # 启动进程并捕获输出
    process = subprocess.Popen([
        admin_script,
        "--port", str(ADMIN_PORT),
        base_dir
    ], cwd=os.path.dirname(admin_script),
       stdout=subprocess.PIPE,
       stderr=subprocess.PIPE,
       universal_newlines=True)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)

    # 返回URL
    local_ip = get_local_ip()
    return {"url": f"http://{local_ip}:{ADMIN_PORT}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 