# ObjectBox Admin Web

一个用于上传和管理 ObjectBox 数据库文件的 Web 应用程序。

## 系统要求

- Python 3.9 或更高版本
- Docker（用于运行 ObjectBox Admin）
- pip（Python 包管理器）

## Python 环境配置

### 1. 安装 Python

#### Windows:
1. 访问 [Python 官网](https://www.python.org/downloads/)
2. 下载 Python 3.9 或更高版本
3. 运行安装程序，确保勾选 "Add Python to PATH"

#### macOS:
1. 使用 Homebrew 安装：
```bash
brew install python@3.9
```
2. 或从 [Python 官网](https://www.python.org/downloads/) 下载安装程序

#### Linux:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9

# CentOS/RHEL
sudo yum install python39
```

### 2. 配置 Python 命令

如果系统同时存在 python/python3 或 pip/pip3 命令，建议创建符号链接：

#### macOS/Linux:
```bash
# 检查当前 Python 版本
python3 --version

# 创建符号链接
sudo ln -sf /usr/local/bin/python3 /usr/local/bin/python
sudo ln -sf /usr/local/bin/pip3 /usr/local/bin/pip
```

#### Windows:
通常安装时会自动配置，如果需要手动配置��
1. 系统属性 -> 环境变量
2. 在 Path 中添加 Python 安装目录

### 3. 验证安装
```bash
# 验证 Python 版本
python --version

# 验证 pip 版本
pip --version
```

## Python 依赖
- FastAPI - Web 框架
- uvicorn - ASGI 服务器
- python-multipart - 用于处理文件上传
- jinja2 - 模板引擎
- aiofiles - 异步文件操作

## 目录结构 
```
project/
├── app.py              # FastAPI 应用主文件
├── templates/          # HTML 模板目录
│   └── index.html     # 上传页面模板
├── objectbox/         # ObjectBox 相关文件目录
│   └── objectbox-admin.sh  # ObjectBox Admin 启动脚本
├── requirements.txt    # Python 依赖文件
└── README.md          # 项目说明文档
```

## 安装步骤

1. 克隆或下载项目到本地：
```bash
git clone <repository-url>
cd <project-directory>
```

2. 创建并激活虚拟环境（可选但推荐）：
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 确保 ObjectBox Admin 脚本有执行权限：
```bash
chmod +x objectbox/objectbox-admin.sh
```

## 运行应用

1. 启动服务器：
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

2. 在浏览器中访问：
```
http://localhost:8000
```

## 使用说明

1. 打开网页后，您会看到一个文件上传界面
2. 点击选择文件，选择要上传的 .mdb 数据库文件
3. 点击 Upload 按钮上传文件
4. 上传成功后，页面会自动跳转到 ObjectBox Admin 界面（端口 8081）

## 注意事项

1. 确保端口 8000（Web 应用）和 8081（ObjectBox Admin）未被其他应用占用
2. 上传的数据库文件会被保存在 objectbox 目录下的唯一子目录中
3. 每次上传新文件时，之前运行的 ObjectBox Admin 实例会被自动关闭
4. 请确保系统已安装 Docker 并且能够正常运行
5. 系统会自动清理超过1分钟的旧文件和目录
6. 清理会在应用启动时和每次上传新文件前执行

## 故障排除

1. 如果遇到权限问题：
   - 确保 objectbox-admin.sh 有执行权限
   - 确保 objectbox 目录有写入权限

2. 如果端口被占用
   - 使用不同的端口启动应用：
     ```bash
     uvicorn app:app --host 0.0.0.0 --port <其他端口号>
     ```
   - 或者关闭占用端口的程序

3. 如果上传后无法跳转：
   - 检查 8081 端口是否被占用
   - 检查 Docker 是否正常运行
   - 查看控制台输出的错误信息

## 开发说明

- app.py：主应用文件，包含所有后端逻辑
  - 使用 FastAPI lifespan 管理应用生命周期
  - 自动处理启动和关闭时的清理工作
- templates/index.html：前端上传界面
- objectbox/：存放 ObjectBox 相关文件和上传的数据库

## 许可证

[添加您的许可证信息]

## 联系方式

[添加您的联系信息]
