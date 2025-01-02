import os
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.database.models import init_db
from app.controllers.instance import router as instance_router
from app.controllers.upload import router as upload_router
from app.controllers.websocket import router as websocket_router
from app.utils.file_utils import cleanup_old_files, stop_existing_container
from app.config import OBJECTBOX_DIR, ADMIN_PORT, FILE_EXPIRE_MINUTES

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

# 创建 FastAPI 应用
app = FastAPI(lifespan=lifespan)

# 配置模板和静态文件
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(instance_router)
app.include_router(upload_router)
app.include_router(websocket_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
