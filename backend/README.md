# FastAPI Backend for Subway Wear Prediction System

## 快速开始

### 环境要求
- Python 3.9+
- PostgreSQL 14+ (生产环境)
- SQLite 3.24+ (开发环境)
- Node.js (用于iFlow CLI)

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

**开发模式:**
```bash
# 使用SQLite作为开发数据库
DATABASE_URL=sqlite:///./subway_wear.db uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**生产模式:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 数据库配置

本项目支持多种数据库系统：

- **开发环境**: 使用SQLite数据库 (推荐)，配置如下：
  ```
  DATABASE_URL=sqlite+aiosqlite:///./subway_wear.db
  ```
  
- **生产环境**: 使用PostgreSQL数据库，配置如下：
  ```
  DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/subway_wear_db
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

## 依赖管理

项目依赖已升级至最新兼容版本，包括：
- FastAPI 0.118.0
- SQLAlchemy 2.0.36
- Pydantic 2.11.10
- Uvicorn 0.37.0
- aiosqlite 0.21.0 (用于SQLite支持)
- 其他相关依赖

## 故障排除

### 常见问题

1. **SQLite数据库错误**: 确保使用 `sqlite+aiosqlite` 作为数据库URL前缀
2. **依赖包错误**: 运行 `pip install -r requirements.txt` 重新安装依赖
3. **API响应错误**: 检查Pydantic模型类型注解是否正确
4. **异步数据库连接错误**: 确保使用了正确的异步驱动 (如asyncpg用于PostgreSQL, aiosqlite用于SQLite)

### 修复历史

- 修复了SQLite异步驱动兼容性问题
- 修复了API响应类型验证错误
- 更新了数据库引擎初始化逻辑以支持多种数据库类型