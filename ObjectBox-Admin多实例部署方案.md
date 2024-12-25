# ObjectBox Admin 多实例部署方案

## 1. 系统架构

### 1.1 基础服务
- Web 服务：FastAPI (端口: 8000)
  * 提供 Web 界面
  * 处理文件上传
  * 管理实例状态

### 1.2 实例架构
每个实例包含：
- Nginx 容器：唯一对外提供服务的入口
- ObjectBox Admin 容器：仅在内部网络可访问
- 独立的 Docker 网络：实现实例隔离

## 2. 网络规划

### 2.1 端口分配
- Web 服务：8000
- 实例端口分配：
  * 实例1：8081
  * 实例2：8082
  * 实例3：8083
  * 实例4：8084
  * 实例5：8085

### 2.2 网络隔离
每个实例使用独立的 Docker 网络：
```
实例1：objectbox-network-1
实例2：objectbox-network-2
实例3：objectbox-network-3
实例4：objectbox-network-4
实例5：objectbox-network-5
```

## 3. 容器配置

### 3.1 Nginx 容器
- 对外端口：8081-8085
- 内部端口：80
- 配置目录挂载
- 反向代理到对应的 Admin 容器

### 3.2 ObjectBox Admin 容器
- 仅内部端口：8081
- 不暴露外部端口
- 数据目录挂载
- 仅接受来自同网络 Nginx 的请求

## 4. 目录结构
```
project_root/
├── app/
├── static/
├── templates/
├── nginx/
│   └── conf.d/
│       └── template.conf    # Nginx配置模板
├── objectbox/
│   ├── instance_1/
│   │   ├── objectbox/      # 实例1数据目录
│   │   │   └── data.mdb
│   │   └── nginx/          # 实例1 Nginx配置
│   │       └── conf.d/
│   │           └── default.conf
│   ├── instance_2/
│   │   ├── objectbox/      # 实例2数据目录
│   │   │   └── data.mdb
│   │   └── nginx/          # 实例2 Nginx配置
│   │       └── conf.d/
│   │           └── default.conf
│   └── ... (instance_3,4,5 同样结构)
└── app.py
```

### 4.1 目录说明
- `/nginx/conf.d/template.conf`: 全局 Nginx 配置模板
- `/objectbox/instance_[1-5]/`: 每个实例的独立目录
  * `objectbox/`: 存放实例数据文件
  * `nginx/`: 存放实例专用的 Nginx 配置

### 4.2 配置生成流程
1. 系统启动时读取全局模板
2. 根据实例ID生成对应配置
3. 配置文件放置在实例专用目录
4. Nginx 容器挂载对应实例的配置目录

## 5. 安全性考虑
- Admin 容器完全隔离，不暴露外部端口
- 每个实例使用独立网络，避免跨实例访问
- 只暴露必要的 Nginx 端口
- 文件系统隔离，避免数据互相影响

## 6. 扩展性
- 端口预留：8086+ 可用于未来扩展
- 网络命名支持动态扩展
- 目录结构支持多实例部署

## 7. 监控和维护
- 容器状态监控
- 网络连接监控
- 日志收集和管理
- 实例状态管理

## 8. 部署流程
1. 创建实例专用网络
2. 启动 Admin 容器
3. 启动 Nginx 容器
4. 验证网络连接
5. 更新实例状态

## 9. 注意事项
- 确保端口未被占用
- 定期清理未使用的网络
- 监控系统资源使用
- 保持配置文件同步 