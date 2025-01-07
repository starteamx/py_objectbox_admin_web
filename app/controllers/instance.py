from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from app.database.manager import DatabaseManager
from app.utils.network import get_local_ip

router = APIRouter()
templates = Jinja2Templates(directory="templates")
db_manager = DatabaseManager()  # 全局数据库管理器实例

@router.get("/")
async def home(request: Request):
    """首页 - 显示所有实例状态"""
    try:
        instances = db_manager.get_all_instances()
        local_ip = get_local_ip()
        
        return templates.TemplateResponse(
            "instance_status.html",
            {
                "request": request,
                "instances": instances,
                "local_ip": local_ip,
                "title": "实例管理"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取实例列表失败: {str(e)}")
    

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

@router.get("/api/instances/status")
async def get_instances_status():
    """获取所有实例的状态"""
    instances = db_manager.get_all_instances()
    return [{
        "instance_id": instance.instance_id,
        "status": instance.status.value,
        "start_time_text": instance.start_time.strftime("%Y-%m-%d %H:%M:%S") if instance.start_time else None,
        "last_active_text": instance.last_active.strftime("%Y-%m-%d %H:%M:%S") if instance.last_active else None
    } for instance in instances] 