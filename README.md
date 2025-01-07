# ObjectBox Admin Web

A web application for uploading and managing ObjectBox database files, supporting parallel multi-instance deployment.

## 1. Project Overview

### 1.1 Features
- Multi-instance parallel operation
- Instance isolation and management
- Web interface for file upload
- Real-time status monitoring
- Automatic resource cleanup

### 1.2 System Architecture
- Web Service: FastAPI (Port: 8000)
  * Web interface
  * File upload handling
  * Instance management
- Instance Architecture:
  * Nginx Container: Single external access point
  * ObjectBox Admin Container: Internal network access only
  * Independent Docker Network: Instance isolation

### 1.3 System Requirements
- Python 3.x Latest Version
- Docker (for running ObjectBox Admin)
- pip (Python Package Manager)
- Mac OS or Linux System

## 2. Project Structure

### 2.1 Core Directory Structure
```
project_root/
├── app/                    # Core application code
│   ├── controllers/        # MVC controllers
│   │   ├── instance.py     # Instance management
│   │   ├── websocket.py    # WebSocket handling
│   │   └── upload.py       # File upload
│   ├── database/          # Database operations
│   │   └── manager.py
│   ├── utils/             # Utility functions
│   │   └── file_utils.py
│   └── config.py          # Configuration file
├── static/                # Static resources
│   ├── css/
│   └── js/
├── templates/             # HTML templates
│   ├── base.html
│   ├── instance_status.html
│   └── instance_upload.html
├── nginx/                 # Nginx configuration
│   └── conf.d/
│       └── template.conf
├── objectbox/             # Instance management
│   ├── instance_1/        # Instance 1
│   │   ├── objectbox/     # Data directory
│   │   └── nginx/         # Config directory
│   ├── instance_2/
│   └── objectbox-admin.sh
├── run/                  # PID files
├── logs/                 # Log files
├── venv/                 # Python virtual environment
├── app.py               # FastAPI main application
├── deploy.sh            # Deployment script
├── stop.sh             # Stop script
└── requirements.txt     # Python dependencies
```

### 2.2 Instance Directory Structure
Each instance contains independent data and configuration directories:
```
instance_N/
├── objectbox/           # Instance data directory
│   └── data.mdb        # Data file
└── nginx/              # Instance Nginx config
    └── conf.d/
        └── default.conf
```

## 3. Installation & Deployment

### 3.1 Basic Environment Setup
1. Python environment configuration
2. Docker environment setup
3. System dependencies installation

### 3.2 Project Deployment
```bash
# 1. Clone project
git clone <repository-url>
cd objectbox-admin-web

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate    # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set permissions
chmod +x deploy.sh stop.sh objectbox/objectbox-admin.sh

# 5. Create necessary directories
mkdir -p run logs
chmod -R 755 run logs

# 6. Start application
./deploy.sh
```

### 3.3 Verify Deployment
```bash
# Check process
ps aux | grep uvicorn

# View logs
tail -f logs/objectbox-admin.log

# Check PID file
cat run/objectbox-admin.pid
```

## 4. Multi-instance Configuration

### 4.1 Network Planning
- Web Service: 8000
- Instance Port Allocation:
  * Instance 1: 8081
  * Instance 2: 8082
  * Instance 3: 8083
  * Instance 4: 8084
  * Instance 5: 8085

### 4.2 Instance Management
```bash
# Create instance network
docker network create objectbox-network-1

# Start instance
./objectbox/objectbox-admin.sh 1  # Start instance 1

# Stop instance
docker rm -f objectbox-admin-1 nginx-1
```

## 5. Maintenance Guide

### 5.1 Routine Maintenance
- Log rotation
- Instance status check
- Resource cleanup

### 5.2 Troubleshooting
```bash
# Check Docker status
docker ps
docker logs <container-id>

# Check network connections
docker network ls
docker network inspect objectbox-network-1

# Clean resources
docker system prune -a
```

## 6. Development Guide

### 6.1 Development Environment Setup
1. Clone repository
2. Install development dependencies
3. Configure development environment

### 6.2 Code Structure
- `app/`: Core application code
- `controllers/`: Request handlers
- `database/`: Data operations
- `utils/`: Utility functions

### 6.3 Testing
```bash
# Unit tests
python -m pytest tests/unit

# Integration tests
python -m pytest tests/integration
```

## 7. Important Notes

### 7.1 Security Recommendations
- Regular dependency updates
- Timely cleanup of expired files
- System resource monitoring

### 7.2 Performance Optimization
- Proper instance count configuration
- Resource usage monitoring
- Regular log cleanup

### 7.3 Common Issues
- Port occupation handling
- Permission issues resolution
- Network connection problems

## 8. License

This project is licensed under the MIT License - see the LICENSE file for details.

## 9. Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request