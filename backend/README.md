# FastAPI Backend for Subway Wear Prediction System

## 快速开始

### 环境要求
- Python 3.9+
- PostgreSQL 14+
- Redis 6+

### 安装步骤

1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，设置数据库连接等配置
```

4. 初始化数据库
```bash
alembic upgrade head
```

5. 运行应用
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API文档

启动应用后访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

详见 [ARCHITECTURE.md](../ARCHITECTURE.md)

## 测试

```bash
pytest tests/ -v
```

## Docker部署

```bash
docker-compose up -d
```

## 开发规范

- 遵循PEP 8代码规范
- 使用Type Hints
- 编写单元测试
- 提交前运行linter和formatter

```bash
black app/
flake8 app/
mypy app/
```