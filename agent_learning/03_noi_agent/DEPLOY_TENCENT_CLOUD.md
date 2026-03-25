# NOI Agent 腾讯云部署手册

> 本文档指导如何在腾讯云服务器上部署 NOI Agent，支持公网访问。

## 部署架构

```
用户 -> Nginx (80/443端口) -> uvicorn (8000端口) -> FastAPI 应用
```

- **Nginx**: 反向代理、静态文件缓存、负载均衡（可选）
- **uvicorn**: ASGI 服务器，运行 FastAPI 应用
- **systemd**: 进程管理，开机自启

## 服务器要求

- **操作系统**: Ubuntu 22.04 LTS
- **CPU**: 1核+
- **内存**: 1GB+
- **磁盘**: 20GB+
- **Python**: 3.11+

## 安全组/防火墙配置

| 端口 | 用途 | 来源 |
|------|------|------|
| 22 | SSH 管理 | 你的 IP |
| 80 | HTTP 访问 | 0.0.0.0/0 |
| 443 | HTTPS 访问（可选） | 0.0.0.0/0 |

**注意**: 8000 端口（uvicorn 直接端口）不应暴露在公网，只让 Nginx 内部访问。

---

## 服务器准备

### 1. 更新系统并安装基础软件

```bash
# SSH 登录服务器后执行
sudo apt update && sudo apt upgrade -y

# 安装必要软件
sudo apt install -y python3.11 python3.11-venv python3-pip nginx git

# 验证安装
python3.11 --version
nginx -v
```

### 2. 创建工作目录

```bash
# 创建应用目录
sudo mkdir -p /opt/noi-agent
cd /opt/noi-agent

# 设置权限（用当前用户部署）
sudo chown -R $USER:$USER /opt/noi-agent
```

---

## 项目部署步骤

### 1. 克隆/上传代码

**方式一：Git 克隆**

```bash
cd /opt/noi-agent
git clone https://github.com/Zrolo/my_agent_project.git .
```

**方式二：手动上传**

```bash
# 本地打包
cd ~/Downloads/my_agent_project/agent_learning/03_noi_agent
tar czvf noi-agent.tar.gz *

# 上传到服务器（在本地执行）
scp noi-agent.tar.gz root@你的服务器IP:/opt/noi-agent/

# 服务器解压
ssh root@你的服务器IP
cd /opt/noi-agent
tar xzvf noi-agent.tar.gz
```

### 2. 创建 Python 虚拟环境

```bash
cd /opt/noi-agent

# 创建虚拟环境
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 验证安装
pip list | grep -E "fastapi|uvicorn|openai"
```

### 3. 配置环境变量

```bash
# 创建 .env 文件
sudo nano /opt/noi-agent/.env
```

填入内容：

```bash
MOONSHOT_API_KEY=你的实际API密钥
```

保存后设置权限：

```bash
# 限制权限，只允许 root 读取
sudo chmod 600 /opt/noi-agent/.env
sudo chown root:root /opt/noi-agent/.env
```

---

## systemd 配置

创建服务文件：

```bash
sudo nano /etc/systemd/system/noi-agent.service
```

填入以下内容：

```ini
[Unit]
Description=NOI Agent FastAPI Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/noi-agent
Environment=PATH=/opt/noi-agent/venv/bin
EnvironmentFile=/opt/noi-agent/.env
ExecStart=/opt/noi-agent/venv/bin/uvicorn api_server:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**说明**:
- `User=www-data`: 使用低权限用户运行
- `--host 127.0.0.1`: 只监听本地，不暴露公网
- `--workers 2`: 根据 CPU 核心数调整（通常 2-4 个）
- `Restart=always`: 崩溃后自动重启

启动服务：

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start noi-agent

# 开机自启
sudo systemctl enable noi-agent

# 查看状态
sudo systemctl status noi-agent
```

---

## Nginx 配置

### 1. 创建配置文件

```bash
sudo nano /etc/nginx/sites-available/noi-agent
```

**无域名版本（IP 访问）**:

```nginx
server {
    listen 80;
    server_name _;  # 接受任何主机名

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**有域名版本**:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/noi-agent /etc/nginx/sites-enabled/

# 删除默认配置（可选）
sudo rm /etc/nginx/sites-enabled/default

# 检查配置语法
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

---

## 验证部署

### 1. 检查服务状态

```bash
# 检查 uvicorn 服务
sudo systemctl status noi-agent

# 检查 Nginx
sudo systemctl status nginx

# 查看端口监听
ss -tlnp | grep -E "80|8000"
```

### 2. 测试接口

```bash
# 测试健康检查（服务器本地）
curl http://localhost:8000/

# 测试健康检查（通过 Nginx）
curl http://localhost/

# 公网测试（在你的电脑执行）
curl http://你的服务器IP/
```

预期返回：

```json
{
  "message": "NOI Coach Agent API is running",
  "hint_limit": 3,
  "version": "0.2.0"
}
```

### 3. 测试前端页面

浏览器访问：

```
http://你的服务器IP/app
```

应看到登录页面。

### 4. 测试完整流程

```bash
# 1. 登录获取 token
curl -X POST http://你的服务器IP/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id":"teacher","password":"password"}'

# 2. 使用 token 查询配额
curl http://你的服务器IP/quota/student_a/P1001 \
  -H "Authorization: Bearer 上一步返回的token"
```

---

## 运维命令

### 查看日志

```bash
# 查看 uvicorn 服务日志
sudo journalctl -u noi-agent -f

# 查看 Nginx 访问日志
sudo tail -f /var/log/nginx/access.log

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/error.log
```

### 重启服务

```bash
# 重启 NOI Agent
sudo systemctl restart noi-agent

# 重启 Nginx
sudo systemctl restart nginx

# 两者一起重启
sudo systemctl restart noi-agent && sudo systemctl restart nginx
```

### 更新代码

```bash
cd /opt/noi-agent

# Git 方式更新
git pull origin master

# 或者重新上传代码后，重启服务
sudo systemctl restart noi-agent
```

### 备份数据

```bash
# 备份 quota.json 和 accounts.json
cd /opt/noi-agent
tar czvf backup-$(date +%Y%m%d).tar.gz quota.json accounts.json

# 下载到本地（在本地执行）
scp root@你的服务器IP:/opt/noi-agent/backup-*.tar.gz ./
```

---

## 故障排查

### 502 Bad Gateway

```bash
# 检查 uvicorn 是否运行
sudo systemctl status noi-agent

# 检查端口是否监听
ss -tlnp | grep 8000

# 查看错误日志
sudo journalctl -u noi-agent -n 50
```

### API Key 错误

```bash
# 检查环境变量
sudo cat /opt/noi-agent/.env

# 检查服务是否读取到
sudo journalctl -u noi-agent | grep -i "API Key"
```

### 权限问题

```bash
# 修复文件权限
sudo chown -R www-data:www-data /opt/noi-agent
sudo chmod 600 /opt/noi-agent/.env
```

---

## 安全建议

1. **尽快配置 HTTPS**: 使用腾讯云 SSL 证书或 Let's Encrypt
2. **限制 SSH 访问**: 安全组只开放你的 IP 访问 22 端口
3. **定期更新系统**: `sudo apt update && sudo apt upgrade -y`
4. **日志监控**: 配置腾讯云 CLS 或自建日志告警

---

## 相关文件

- `api_server.py`: FastAPI 主应用
- `noi_agent.py`: 核心配额逻辑
- `auth.py`: 认证逻辑
- `accounts.json`: 用户账号
- `quota.json`: 配额数据
- `.env`: 环境变量（包含 API Key）
