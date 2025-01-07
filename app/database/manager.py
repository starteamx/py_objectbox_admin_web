import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from .models import Instance, InstanceStatus

class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 使用项目根目录下的 data 目录
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(root_dir, "data")
            os.makedirs(data_dir, exist_ok=True)  # 确保目录存在
            self.db_path = os.path.join(data_dir, "instance.db")
        else:
            self.db_path = db_path
        self.init_database()

    def get_instance(self, instance_id: int) -> Optional[Instance]:
        """获取单个实例信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, instance_id, port, status, start_time, last_active
                FROM instances 
                WHERE instance_id = ?
            """, (instance_id,))
            row = cursor.fetchone()
            
            if row:
                return Instance(
                    id=row[0],
                    instance_id=row[1],
                    port=row[2],
                    status=InstanceStatus(row[3]),
                    start_time=datetime.fromisoformat(row[4]) if row[4] else None,
                    last_active=datetime.fromisoformat(row[5]) if row[5] else None
                )
            return None

    def update_instance_status(
        self, 
        instance_id: int, 
        status: InstanceStatus,
        start_time: Optional[datetime] = None
    ) -> bool:
        """更新实例状态"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if start_time:
                    cursor.execute("""
                        UPDATE instances 
                        SET status = ?, start_time = ?, last_active = ?
                        WHERE instance_id = ?
                    """, (
                        status.value,
                        start_time.isoformat(),
                        datetime.now().isoformat(),
                        instance_id
                    ))
                else:
                    cursor.execute("""
                        UPDATE instances 
                        SET status = ?, last_active = ?
                        WHERE instance_id = ?
                    """, (
                        status.value,
                        datetime.now().isoformat(),
                        instance_id
                    ))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating instance status: {e}")
            return False

    def get_all_instances(self) -> List[Instance]:
        """获取所有实例信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, instance_id, port, status, start_time, last_active
                FROM instances
                ORDER BY instance_id
            """)
            return [
                Instance(
                    id=row[0],
                    instance_id=row[1],
                    port=row[2],
                    status=InstanceStatus(row[3]),
                    start_time=datetime.fromisoformat(row[4]) if row[4] else None,
                    last_active=datetime.fromisoformat(row[5]) if row[5] else None
                )
                for row in cursor.fetchall()
            ]

    def init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS instances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    instance_id INTEGER UNIQUE NOT NULL,
                    port INTEGER NOT NULL,
                    status INTEGER NOT NULL DEFAULT 0,
                    start_time TEXT,
                    last_active TEXT
                )
            """)
            conn.commit()

    def reset_all_instances(self):
        """重置所有实例状态"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE instances 
                SET status = ?, start_time = NULL, last_active = ?
            """, (InstanceStatus.IDLE.value, datetime.now().isoformat()))
            conn.commit()
