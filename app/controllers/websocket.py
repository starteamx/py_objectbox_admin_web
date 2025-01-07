from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime
from app.database.manager import DatabaseManager
from app.database.models import InstanceStatus
from app.utils.file_utils import stop_instance_container
import os
import shutil

router = APIRouter()
db_manager = DatabaseManager()

# 心跳配置
HEARTBEAT_TIMEOUT = 30  # 心跳超时时间（秒）
HEARTBEAT_INTERVAL = 15  # 心跳间隔时间（秒）

class InstanceWebsocketManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}  # 每个实例只保持一个连接
    
    async def connect(self, instance_id: int, websocket: WebSocket):
        """建立新连接，如果已存在则关闭旧连接"""
        if instance_id in self.active_connections:
            try:
                await self.active_connections[instance_id].close()
            except:
                pass
        await websocket.accept()
        self.active_connections[instance_id] = websocket
    
    async def disconnect(self, instance_id: int):
        """断开连接并清理"""
        if instance_id in self.active_connections:
            try:
                await self.active_connections[instance_id].close()
            except:
                pass
            del self.active_connections[instance_id]
            await handle_instance_cleanup(instance_id)

async def handle_instance_cleanup(instance_id: int):
    """处理实例清理"""
    try:
        print(f"Starting cleanup for instance {instance_id}")
        
        # 停止容器
        stop_instance_container(instance_id)
        
        # 清理实例目录
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        instance_dir = os.path.join(root_dir, "objectbox", f"instance_{instance_id}")
        if os.path.exists(instance_dir):
            try:
                shutil.rmtree(instance_dir)
                print(f"Cleaned up instance directory: {instance_dir}")
            except Exception as e:
                print(f"Error cleaning up directory {instance_dir}: {e}")
        
        # 更新状态
        instance = db_manager.get_instance(instance_id)
        if instance:
            db_manager.update_instance_status(
                instance_id,
                InstanceStatus.IDLE,
                None  # 清除启动时间
            )
        
        print(f"Cleanup completed for instance {instance_id}")
    except Exception as e:
        print(f"Error during cleanup for instance {instance_id}: {e}")

async def send_heartbeat(websocket: WebSocket):
    """发送心跳消息"""
    try:
        while True:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            await websocket.send_json({
                "type": "ping",
                "timestamp": datetime.now().isoformat()
            })
    except asyncio.CancelledError:
        pass

@router.websocket("/ws/{instance_id}")
async def websocket_endpoint(websocket: WebSocket, instance_id: int):
    """WebSocket连接端点"""
    try:
        # 验证实例
        instance = db_manager.get_instance(instance_id)
        if not instance or instance.status != InstanceStatus.RUNNING:
            await websocket.close(code=4004)
            return
        
        # 建立连接
        await manager.connect(instance_id, websocket)
        print(f"WebSocket connection established for instance {instance_id}")
        
        # 记录最后心跳时间
        last_heartbeat = datetime.now()
        
        # 启动心跳任务
        heartbeat_task = asyncio.create_task(send_heartbeat(websocket))
        
        try:
            while True:
                try:
                    # 等待消息，设置超时
                    data = await asyncio.wait_for(
                        websocket.receive_text(),
                        timeout=HEARTBEAT_TIMEOUT
                    )
                    message = json.loads(data)
                    
                    if message.get('type') == 'pong':
                        last_heartbeat = datetime.now()
                    
                except asyncio.TimeoutError:
                    print(f"Instance {instance_id} heartbeat timeout")
                    break
                    
        except WebSocketDisconnect:
            print(f"WebSocket disconnected for instance {instance_id}")
            
    except Exception as e:
        print(f"WebSocket error for instance {instance_id}: {e}")
        
    finally:
        # 清理连接和资源
        if 'heartbeat_task' in locals():
            heartbeat_task.cancel()
        await manager.disconnect(instance_id)
        print(f"WebSocket connection closed for instance {instance_id}")

manager = InstanceWebsocketManager()