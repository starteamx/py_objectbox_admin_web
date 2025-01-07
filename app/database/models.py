from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from enum import IntEnum

class InstanceStatus(IntEnum):
    """实例状态枚举"""
    IDLE = 0        # 空闲
    RUNNING = 1     # 运行中
    
    @classmethod
    def to_string(cls, status: int) -> str:
        """状态码转换为文本"""
        return {
            cls.IDLE: "空闲",
            cls.RUNNING: "运行中"
        }.get(status, "未知")

@dataclass
class Instance:
    """实例对象"""
    id: int                       # 数据库自增ID
    instance_id: int              # 实例ID (1-5)
    port: int                     # 端口号
    status: InstanceStatus        # 状态枚举
    start_time: Optional[datetime] # 启动时间
    last_active: Optional[datetime] # 最后活跃时间
    
    @property
    def status_text(self) -> str:
        """获取状态文本"""
        return InstanceStatus.to_string(self.status)
    
    @property
    def start_time_text(self) -> str:
        """获取格式化的启动时间"""
        return self.start_time.strftime("%Y-%m-%d %H:%M:%S") if self.start_time else "-"
    
    @property
    def last_active_text(self) -> str:
        """获取格式化的最后活跃时间"""
        return self.last_active.strftime("%Y-%m-%d %H:%M:%S") if self.last_active else "-"
