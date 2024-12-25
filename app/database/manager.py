from datetime import datetime
from typing import List, Optional
from .models import Instance, Session, VirtualUser, InstanceLog, get_db

class DatabaseManager:
    @staticmethod
    def get_all_instances() -> List[Instance]:
        """获取所有实例状态"""
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM instances ORDER BY id')
        instances = cursor.fetchall()
        db.close()
        return [Instance.from_db_row(dict(row)) for row in instances]

    @staticmethod
    def get_instance(instance_id: int) -> Optional[Instance]:
        """获取单个实例信息"""
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM instances WHERE id = ?', (instance_id,))
        row = cursor.fetchone()
        db.close()
        return Instance.from_db_row(dict(row)) if row else None

    @staticmethod
    def update_instance_status(instance_id: int, status: str, container_id: Optional[str] = None):
        """更新实例状态"""
        db = get_db()
        cursor = db.cursor()
        now = datetime.now()
        
        if status == 'RUNNING':
            cursor.execute('''
            UPDATE instances 
            SET status = ?, start_time = ?, last_active = ?, container_id = ?
            WHERE id = ?
            ''', (status, now, now, container_id, instance_id))
        else:
            cursor.execute('''
            UPDATE instances 
            SET status = ?, start_time = NULL, last_active = NULL, container_id = NULL
            WHERE id = ?
            ''', (status, instance_id))
        
        db.commit()
        db.close()

    @staticmethod
    def log_activity(instance_id: int, user_id: Optional[int], 
                    session_id: Optional[str], action: str, details: Optional[str]) -> InstanceLog:
        """记录实例活动"""
        db = get_db()
        cursor = db.cursor()
        now = datetime.now()
        cursor.execute('''
        INSERT INTO instance_logs (instance_id, user_id, session_id, action, timestamp, details)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (instance_id, user_id, session_id, action, now, details))
        
        log_id = cursor.lastrowid
        cursor.execute('SELECT * FROM instance_logs WHERE id = ?', (log_id,))
        log = cursor.fetchone()
        
        db.commit()
        db.close()
        
        return InstanceLog.from_db_row(dict(log))
