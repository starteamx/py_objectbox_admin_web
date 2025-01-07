class InstanceMonitor {
    constructor(instanceId, wsUrl) {
        this.instanceId = instanceId;
        this.wsUrl = wsUrl;
        this.ws = null;
        this.adminWindow = null;
        this.checkWindowInterval = null;
        this.setupWebSocket();
    }

    setupWebSocket() {
        console.log('Setting up WebSocket connection...');
        setTimeout(() => {
            try {
                this.ws = new WebSocket(this.wsUrl);
                
                this.ws.onopen = () => {
                    console.log('WebSocket connected');
                    document.getElementById('connectionStatus').textContent = '已连接';
                    document.getElementById('connectionStatus').style.color = 'green';
                };

                this.ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    if (data.type === 'ping') {
                        this.ws.send(JSON.stringify({
                            type: 'pong',
                            timestamp: new Date().toISOString()
                        }));
                    }
                };

                this.ws.onclose = () => {
                    console.log('WebSocket disconnected');
                    this.cleanup();
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.cleanup();
                };
                
            } catch (error) {
                console.error('Error creating WebSocket:', error);
                this.cleanup();
            }
        }, 5000);
    }

    openAdminWindow(url) {
        this.adminWindow = window.open('', '_blank');
        this.adminWindow.document.write(this.getLoadingHtml());
        
        // 开始检查窗口状态
        this.checkWindowInterval = setInterval(() => {
            if (this.adminWindow.closed) {
                this.cleanup();
            }
        }, 1000);

        setTimeout(() => {
            if (this.adminWindow && !this.adminWindow.closed) {
                this.adminWindow.location.href = url;
            }
        }, 5000);
    }

    cleanup() {
        // 清理 WebSocket
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        // 清理窗口检查定时器
        if (this.checkWindowInterval) {
            clearInterval(this.checkWindowInterval);
        }

        // 关闭管理窗口
        if (this.adminWindow && !this.adminWindow.closed) {
            this.adminWindow.close();
        }

        // 返回实例列表
        window.location.href = '/';
    }

    getLoadingHtml() {
        return `
        <!DOCTYPE html>
        <html>
        <head>
            <title>加载中...</title>
            <style>
                body {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                    font-family: Arial, sans-serif;
                }
                .spinner {
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #3498db;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin-bottom: 20px;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        </head>
        <body>
            <div class="spinner"></div>
            <h3>正在启动 ObjectBox Admin...</h3>
            <p>请稍候，这可能需要几秒钟的时间</p>
        </body>
        </html>`;
    }
} 