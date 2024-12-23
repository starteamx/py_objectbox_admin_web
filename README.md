# ObjectBox Admin Web

一个用于上传和管理 ObjectBox 数据库文件的 Web 应用程序。

## 系统要求

- Python 3.9 或更高版本
- Docker（用于运行 ObjectBox Admin）
- pip（Python 包管理器）

## 安装说明

### 1. 克隆项目
```bash
git clone <repository-url>
cd objectbox-admin-web
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 准备目录结构
```
project/
├── app.py              # FastAPI 主应用
├── static/             # 静态文件目录
├── templates/          # HTML 模板目录
│   └── index.html     # 上传页面
├── objectbox/          # ObjectBox 相关文件
│   ├── nginx/         # Nginx 配置目录
│   └── objectbox-admin.sh  # 启动脚本
└── requirements.txt    # Python 依赖
```

## 使用说明

### 启动服务
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

### 访问界面
- 本地访问：http://localhost:8000
- 局域网访问：http://<your-ip>:8000

## 关键功能点

### Docker 网络配置
- 使用自定义网络 `objectbox-network`
- 容器间通过容器名称通信
- 固定容器名称确保稳定性

### Nginx 代理设置
- 使用容器名称作为上游服务器
- 配置正确的代理头信息
- 启用详细的错误日志

### 容器管理机制
- 自动清理旧容器
- 使用固定容器名称
- 正确的启动和清理顺序

## 注意事项

### 权限设置
- 确保 objectbox-admin.sh 有执行权限
- 确保 objectbox 目录有写入权限

### 端口占用
- 默认使用 8000 端口（Web 应用）
- 默认使用 8081 端口（ObjectBox Admin）
- 可通过参数修改端口号

### 文件清理
- 自动清理过期文件
- 保留必要的配置文件
- 可配置清理时间间隔

## 故障排除

### 1. 容器启动失败
```bash
# 检查 Docker 日志
docker logs objectbox-admin
docker logs nginx-proxy
```

### 2. 网络连接问题
```bash
# 检查网络配置
docker network inspect objectbox-network
```

### 3. 权限问题
```bash
# 设置执行权限
chmod +x objectbox/objectbox-admin.sh
```

## 许可证

[添加您的许可证信息]

## 联系方式

[添加您的联系信息]
