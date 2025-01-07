import os
import shutil
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.database.manager import DatabaseManager
from app.controllers import instance, websocket, upload
from app.utils.file_utils import stop_instance_container

def cleanup_all_instances():
    """清理所有实例的目录和容器"""
    try:
        # 获取所有实例
        db_manager = DatabaseManager()
        instances = db_manager.get_all_instances()
        
        # 清理每个实例
        for instance in instances:
            # 停止容器
            stop_instance_container(instance.instance_id)
            
            # 清理实例目录
            root_dir = os.path.dirname(os.path.abspath(__file__))
            instance_dir = os.path.join(root_dir, "objectbox", f"instance_{instance.instance_id}")
            if os.path.exists(instance_dir):
                try:
                    shutil.rmtree(instance_dir)
                    print(f"Cleaned up instance directory: {instance_dir}")
                except Exception as e:
                    print(f"Error cleaning up directory {instance_dir}: {e}")

        # 重置所有实例状态
        db_manager.reset_all_instances()
        print("All instances cleaned up")
    except Exception as e:
        print(f"Error during cleanup: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用的生命周期管理"""
    # 启动时执行
    db_manager = DatabaseManager()
    db_manager.init_database()
    cleanup_all_instances()
    
    yield
    
    # 关闭时执行
    cleanup_all_instances()

# 创建 FastAPI 应用
app = FastAPI(lifespan=lifespan)

# 配置模板和静态文件
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(instance.router)
app.include_router(upload.router)
app.include_router(websocket.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
