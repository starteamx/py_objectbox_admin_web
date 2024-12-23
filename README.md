# ObjectBox Admin Web

一个用于上传和管理 ObjectBox 数据库文件的 Web 应用程序。

## 系统要求

- Python 3.x 最新版本
- Docker（用于运行 ObjectBox Admin）
- pip（Python 包管理器）
- Mac OS 或 Linux 系统

## Python 安装说明

### Windows 安装
1. **下载安装包**
   - 访问 [Python 官网](https://www.python.org/downloads/)
   - 下载最新版本的 Windows 安装包（选择 64 位版本）

2. **安装步骤**
```bash
# 运行安装包，注意勾选：
# - Install launcher for all users
# - Add Python to PATH
```

3. **验证安装**
```bash
python --version
pip --version
```

### Mac OS 安装

1. **使用 Homebrew 安装**
```bash
# 安装 Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装最新版本 Python
brew install python

# 验证安装
python3 --version
pip3 --version
```

### Linux 安装

#### Ubuntu/Debian
```bash
# 更新包列表
sudo apt update

# 安装 Python
sudo apt install -y python3 python3-pip python3-venv

# 验证安装
python3 --version
pip3 --version
```

#### CentOS/RHEL
```bash
# 安装 Python
sudo dnf install -y python3 python3-pip

# 验证安装
python3 --version
pip3 --version
```

### 验证 Python 环境
```bash
# 检查 Python 版本
python3 --version

# 检查 pip 版本
pip3 --version

## Python 命令重命名

### Windows 系统

1. **创建命令别名**
```batch
# 创建 .bat 文件
# C:\Windows\System32\python.bat
@echo off
python3 %*

# C:\Windows\System32\pip.bat
@echo off
pip3 %*
```

### Mac/Linux 系统

1. **Bash 用户**
```bash
# 编辑 ~/.bashrc
echo 'alias python=python3' >> ~/.bashrc
echo 'alias pip=pip3' >> ~/.bashrc

# 重新加载配置
source ~/.bashrc
```

2. **Zsh 用户（Mac 默认）**
```bash
# 编辑 ~/.zshrc
echo 'alias python=python3' >> ~/.zshrc
echo 'alias pip=pip3' >> ~/.zshrc

# 重新加载配置
source ~/.zshrc
```

### 验证设置
```bash
# 检查 Python 版本
python --version

# 检查 pip 版本
pip --version
```

## 安装说明

### 1. 克隆项目
```bash
git clone <repository-url>
cd objectbox-admin-web
```

### 2. 创建并激活虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 确认虚拟环境已激活（命令行前会出现 (venv) 标识）
python --version
```

### 3. 安装依赖
```bash
# 确保在虚拟环境中
pip install -r requirements.txt
```

### 4. 准备目录结构
```
project/
├── app.py              # FastAPI 主应用
├── deploy.sh           # 部署脚本
├── stop.sh            # 停止脚本
├── static/            # 静态文件目录
├── templates/         # HTML 模板目录
│   └── index.html    # 上传页面
├── objectbox/         # ObjectBox 相关文件
│   ├── nginx/        # Nginx 配置目录
│   └── objectbox-admin.sh  # 启动脚本
├── run/              # PID 文件目录
├── logs/             # 日志文件目录
├── venv/             # Python 虚拟环境
└── requirements.txt   # Python 依赖
```

## 部署说明

### 1. 设置脚本权限
```bash
chmod +x deploy.sh stop.sh objectbox/objectbox-admin.sh
```

### 2. 创建必要目录
```bash
# 创建日志和PID文件目录
mkdir -p run logs
chmod -R 755 run logs
```

### 3. 启动应用
```bash
# 确保在虚拟环境中
source venv/bin/activate  # Mac/Linux
# 或
venv\Scripts\activate    # Windows

# 启动应用
./deploy.sh
```

### 4. 查看运行状态
```bash
# 查看进程
ps aux | grep uvicorn

# 查看日志
tail -f logs/objectbox-admin.log

# 查看 PID 文件
cat run/objectbox-admin.pid
```

### 5. 停止应用
```bash
./stop.sh

# 如果需要，退出虚拟环境
deactivate
```

### 6. 更新依赖（如需）
```bash
# 确保在虚拟环境中
source venv/bin/activate  # Mac/Linux
# 或
venv\Scripts\activate    # Windows

# 更新依赖
pip install -r requirements.txt

# 如果添加了新的依赖，更新 requirements.txt
pip freeze > requirements.txt
```

## 注意事项

### 虚拟环境管理
- 始终在虚拟环境中运行应用
- 定期更新 requirements.txt
- 不要将 venv 目录提交到代码仓库

### 权限设置
- 确保所有 .sh 文件有执行权限
- 确保 objectbox 目录有写入权限
- 确保 logs 和 run 目录可写
- 确保虚拟环境目录权限正确

### Git 配置
```bash
# 将虚拟环境添加到 .gitignore
echo "venv/" >> .gitignore
echo "run/" >> .gitignore
echo "logs/" >> .gitignore
```

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

### 3. 应用启动问题
```bash
# 检查应用日志
tail -f logs/objectbox-admin.log

# 检查进程状态
ps aux | grep uvicorn
```

### 4. 权限问题
```bash
# 设置执行权限
chmod +x deploy.sh stop.sh objectbox/objectbox-admin.sh

# 设置目录权限
chmod -R 755 logs run
```

## 许可证

[添加您的许可证信息]

## 联系方式

[添加您的联系信息]
