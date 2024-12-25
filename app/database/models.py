from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Instance:
    id: int
    port: int
    status: str
    start_time: Optional[datetime] = None
    last_active: Optional[datetime] = None
    session_id: Optional[str] = None
    container_id: Optional[str] = None

    @classmethod
    def from_db_row(cls, row: dict):
        """从数据库行创建实例"""
        return cls(
            id=row['id'],
            port=row['port'],
            status=row['status'],
            start_time=datetime.fromisoformat(row['start_time']) if row['start_time'] else None,
            last_active=datetime.fromisoformat(row['last_active']) if row['last_active'] else None,
            session_id=row['session_id'],
            container_id=row['container_id']
        )

@dataclass
class Session:
    id: str
    user_id: int
    instance_id: int
    created_at: datetime
    last_active: datetime

    @classmethod
    def from_db_row(cls, row: dict):
        return cls(
            id=row['id'],
            user_id=row['user_id'],
            instance_id=row['instance_id'],
            created_at=datetime.fromisoformat(row['created_at']),
            last_active=datetime.fromisoformat(row['last_active'])
        )

@dataclass
class VirtualUser:
    id: int
    ip_address: str
    user_agent: str
    first_visit: datetime
    last_visit: datetime
    visit_count: int

    @classmethod
    def from_db_row(cls, row: dict):
        return cls(
            id=row['id'],
            ip_address=row['ip_address'],
            user_agent=row['user_agent'],
            first_visit=datetime.fromisoformat(row['first_visit']),
            last_visit=datetime.fromisoformat(row['last_visit']),
            visit_count=row['visit_count']
        )

@dataclass
class InstanceLog:
    id: int
    instance_id: int
    user_id: Optional[int]
    session_id: Optional[str]
    action: str
    timestamp: datetime
    details: Optional[str]

    @classmethod
    def from_db_row(cls, row: dict):
        return cls(
            id=row['id'],
            instance_id=row['instance_id'],
            user_id=row['user_id'],
            session_id=row['session_id'],
            action=row['action'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            details=row['details']
        )

# 数据库初始化代码
import sqlite3
import os

# 数据库文件路径
DB_PATH = "data/objectbox.db"

# 确保数据目录存在
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    """初始化数据库表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 创建实例表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS instances (
        id INTEGER PRIMARY KEY,
        port INTEGER UNIQUE,
        status TEXT CHECK(status IN ('IDLE', 'RUNNING')),
        start_time DATETIME,
        last_active DATETIME,
        session_id TEXT,
        container_id TEXT
    )''')

    # 创建会话表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        user_id INTEGER,
        instance_id INTEGER,
        created_at DATETIME NOT NULL,
        last_active DATETIME NOT NULL
    )''')

    # 创建虚拟用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS virtual_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT NOT NULL,
        user_agent TEXT,
        first_visit DATETIME NOT NULL,
        last_visit DATETIME NOT NULL,
        visit_count INTEGER DEFAULT 1
    )''')

    # 创建实例活动日志表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS instance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instance_id INTEGER NOT NULL,
        user_id INTEGER,
        session_id TEXT,
        action TEXT NOT NULL,
        timestamp DATETIME NOT NULL,
        details TEXT
    )''')

    # 初始化 5 个实例数据
    cursor.execute('SELECT COUNT(*) FROM instances')
    if cursor.fetchone()[0] == 0:
        for i in range(1, 6):
            cursor.execute('''
            INSERT INTO instances (id, port, status, start_time, last_active)
            VALUES (?, ?, 'IDLE', NULL, NULL)
            ''', (i, 8080 + i))

    conn.commit()
    conn.close()

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
