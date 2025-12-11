部署指南文件已创建
# 地铁车辆磨耗预测系统 - 部署指南

## 部署选项

### 选项1：Docker Compose 部署（推荐）

确保服务器上已安装 Docker 和 Docker Compose：

```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

克隆项目代码到服务器：

```bash
git clone https://github.com/pcwto2025/subway-wear-prediction.git
cd subway-wear-prediction
```

使用提供的 docker-compose.yml 配置文件启动服务：

```bash
docker-compose up -d
```

### 选项2：手动部署

后端部署：

```bash
# 安装 Python 3.9+
git clone https://github.com/pcwto2025/subway-wear-prediction.git
cd subway-wear-prediction/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

前端部署：

```bash
cd frontend
npm install
npm run build
# 使用 Nginx 部署 dist 目录中的文件
```

## 生产环境配置要点

1. **安全性**：使用强密码和密钥，配置 HTTPS，设置防火墙
2. **数据库**：使用 PostgreSQL 而不是 SQLite，定期备份
3. **性能**：使用反向代理（Nginx），启用缓存（Redis）
4. **监控**：设置日志记录，配置错误追踪

部署完成后，访问 http://your-server-ip:8000 来使用系统。
