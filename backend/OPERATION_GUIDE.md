# 地铁车辆磨耗预测系统 - 操作指南

## 项目概述

地铁车辆磨耗预测系统是一个基于FastAPI的智能预测平台，用于预测地铁车辆关键部件的磨耗情况，并提供维护建议和风险评估。

## 环境要求

- Python 3.9+
- Node.js (用于iFlow CLI)

## 安装步骤

### 1. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env
# 编辑 .env 文件，根据需要修改配置
```

### 4. 运行应用

```bash
# 启动服务（使用SQLite作为开发数据库）
DATABASE_URL=sqlite:///./subway_wear.db uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API端点

### 基础端点

- `GET /` - 系统信息
- `GET /health` - 健康检查
- `GET /docs` - API文档 (Swagger UI)
- `GET /redoc` - API文档 (ReDoc)

### API端点

- `GET /api/v1` - API信息
- `POST /api/v1/predictions/single` - 单车磨耗预测
- `POST /api/v1/predictions/batch` - 批量车辆预测
- `GET /api/v1/predictions/trends` - 磨耗趋势

## 项目结构

```
app/
├── main.py          # 主应用文件
├── config.py        # 配置管理
├── api/             # API端点
│   └── v1/          # API v1版本
├── core/            # 核心功能
│   └── database.py  # 数据库配置
├── models/          # 数据模型
├── schemas/         # Pydantic模型
├── services/        # 业务逻辑
└── utils/           # 工具函数
```

## 开发说明

### 数据库配置

- 开发环境使用SQLite数据库 (`sqlite:///./subway_wear.db`)
- 生产环境使用PostgreSQL数据库
- 数据库配置通过环境变量 `DATABASE_URL` 控制

### 依赖管理

项目依赖已升级至最新兼容版本，包括：
- FastAPI 0.118.0
- SQLAlchemy 2.0.36
- Pydantic 2.11.10
- Uvicorn 0.37.0
- 其他相关依赖

### 运行测试

```bash
pytest tests/ -v
```

## 故障排除

### 常见问题

1. **数据库连接错误**：确保环境变量 `DATABASE_URL` 配置正确
2. **依赖包错误**：运行 `pip install -r requirements.txt` 重新安装依赖
3. **API响应错误**：检查Pydantic模型类型注解是否正确

### 修复历史

- 修复了SQLite异步驱动兼容性问题
- 修复了API响应类型验证错误
- 更新了数据库引擎初始化逻辑以支持多种数据库类型

## 维护建议

- 定期更新依赖包以获得最新功能和安全补丁
- 在生产环境中使用PostgreSQL数据库
- 配置适当的日志记录和监控
- 定期备份数据库