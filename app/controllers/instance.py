from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from app.database.manager import DatabaseManager
from app.utils.network import get_local_ip
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")
db_manager = DatabaseManager()

@router.get("/")
async def home(request: Request):
    """首页 - 显示所有实例状态"""
    instances = db_manager.get_all_instances()
    local_ip = get_local_ip()
    
    # 处理实例数据以适应模板
    instances_data = []
    for instance in instances:
        instance_dict = {
            "id": instance.id,
            "port": 8080 + instance.id,
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
            instance_dict["time_percentage"] = min((running_time.seconds / 1800) * 100, 100)
        
        instances_data.append(instance_dict)
    
    return templates.TemplateResponse(
        "instance_status.html",
        {
            "request": request, 
            "instances": instances_data,
            "local_ip": local_ip
        }
    )

@router.get("/instance/{instance_id}")
async def instance_detail(request: Request, instance_id: int):
    """实例详情页面"""
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