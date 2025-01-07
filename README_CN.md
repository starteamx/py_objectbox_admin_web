# ObjectBox Admin Web

一个用于上传和管理 ObjectBox 数据库文件的 Web 应用程序，支持多实例并行部署。

## 1. 项目概述

### 1.1 功能特点
- 多实例并行运行
- 实例隔离与管理
- Web界面文件上传
- 实时状态监控
- 自动资源清理

### 1.2 系统架构
- Web 服务：FastAPI (端口: 8000)
  * 提供 Web 界面
  * 处理文件上传
  * 管理实例状态
- 实例架构：
  * Nginx 容器：唯一对外提供服务的入口
  * ObjectBox Admin 容器：仅在内部网络可访问
  * 独立的 Docker 网络：实现实例隔离

### 1.3 系统要求
- Python 3.x 最新版本
- Docker（用于运行 ObjectBox Admin）
- pip（Python 包管理器）
- Mac OS 或 Linux 系统

## 2. 项目结构

### 2.1 核心目录结构
```
project_root/
├── app/                    # 应用核心代码
│   ├── controllers/        # MVC控制器
│   │   ├── instance.py     # 实例管理
│   │   ├── websocket.py    # WebSocket处理
│   │   └── upload.py       # 文件上传
│   ├── database/          # 数据库操作
│   │   └── manager.py
│   ├── utils/             # 工具函数
│   │   └── file_utils.py
│   └── config.py          # 配置文件
├── static/                # 静态资源
│   ├── css/
│   └── js/
├── templates/             # HTML模板
│   ├── base.html
│   ├── instance_status.html
│   └── instance_upload.html
├── nginx/                 # Nginx配置
│   └── conf.d/
│       └── template.conf
├── objectbox/             # 实例管理
│   ├── instance_1/        # 实例1
│   │   ├── objectbox/     # 数据目录
│   │   └── nginx/         # 配置目录
│   ├── instance_2/
│   └── objectbox-admin.sh
├── run/                  # PID文件
├── logs/                 # 日志文件
├── venv/                 # Python虚拟环境
├── app.py               # FastAPI主应用
├── deploy.sh            # 部署脚本
├── stop.sh             # 停止脚本
└── requirements.txt     # Python依赖
```

### 2.2 实例目录结构
每个实例包含独立的数据和配置目录：
```
instance_N/
├── objectbox/           # 实例数据目录
│   └── data.mdb        # 数据文件
└── nginx/              # 实例Nginx配置
    └── conf.d/
        └── default.conf
```

## 3. 安装部署

### 3.1 基础环境配置
1. Python 环境配置
2. Docker 环境配置
3. 系统依赖安装

### 3.2 项目部署
```bash
# 1. 克隆项目
git clone <repository-url>
cd objectbox-admin-web

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate    # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 设置权限
chmod +x deploy.sh stop.sh objectbox/objectbox-admin.sh

# 5. 创建必要目录
mkdir -p run logs
chmod -R 755 run logs

# 6. 启动应用
./deploy.sh
```

### 3.3 验证部署
```bash
# 检查进程
ps aux | grep uvicorn

# 查看日志
tail -f logs/objectbox-admin.log

# 检查PID文件
cat run/objectbox-admin.pid
```

## 4. 多实例配置

### 4.1 网络规划
- Web 服务：8000
- 实例端口分配：
  * 实例1：8081
  * 实例2：8082
  * 实例3：8083
  * 实例4：8084
  * 实例5：8085

### 4.2 实例管理
```bash
# 创建实例网络
docker network create objectbox-network-1

# 启动实例
./objectbox/objectbox-admin.sh 1  # 启动实例1

# 停止实例
docker rm -f objectbox-admin-1 nginx-1
```

## 5. 维护指南

### 5.1 日常维护
- 日志轮转
- 实例状态检查
- 资源清理

### 5.2 故障排除
```bash
# 检查Docker状态
docker ps
docker logs <container-id>

# 检查网络连接
docker network ls
docker network inspect objectbox-network-1

# 清理资源
docker system prune -a
```

## 6. 开发指南

### 6.1 开发环境设置
1. 克隆代码库
2. 安装开发依赖
3. 配置开发环境

### 6.2 代码结构说明
- `app/`: 核心应用代码
- `controllers/`: 请求处理
- `database/`: 数据操作
- `utils/`: 工具函数

### 6.3 测试运行
```bash
# 单元测试
python -m pytest tests/unit

# 集成测试
python -m pytest tests/integration
```

## 7. 注意事项

### 7.1 安全建议
- 定期更新依赖
- 及时清理过期文件
- 监控系统资源

### 7.2 性能优化
- 合理配置实例数量
- 监控资源使用
- 定期清理日志

### 7.3 常见问题
- 端口占用处理
- 权限问题解决
- 网络连接问题