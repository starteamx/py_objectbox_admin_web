import os
import shutil
import subprocess
import time
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.database.manager import DatabaseManager
from app.utils.network import get_local_ip

router = APIRouter()
db_manager = DatabaseManager()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    instance_id: int = Form(...)
):
    """处理文件上传并启动实例"""
    if not file.filename.endswith('.mdb'):
        raise HTTPException(status_code=400, detail="只接受 .mdb 文件")
    
    try:
        instance = db_manager.get_instance(instance_id)
        if not instance or instance.status == 'RUNNING':
            raise HTTPException(status_code=400, detail="实例不可用")

        # 使用项目根目录
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
        
        # 启动服务
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
        
        time.sleep(5)  # 等待服务启动
        
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