# 项目架构设计文档
# 地铁车辆磨耗预测系统 - FastAPI架构

## 1. 系统架构概览

```
┌─────────────────────────────────────────────────────────┐
│                     前端应用层                           │
│  Vue.js/React + TypeScript + Tailwind CSS               │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS/WebSocket
┌────────────────────▼────────────────────────────────────┐
│                   API网关层                              │
│         Nginx (反向代理, 负载均衡, 限流)                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  应用服务层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   FastAPI    │  │   FastAPI    │  │   FastAPI    │ │
│  │   主服务     │  │  预测服务    │  │  数据服务    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  业务逻辑层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ 车辆管理模块 │  │ 预测算法模块 │  │ 报表生成模块 │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   数据访问层                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  PostgreSQL  │  │    Redis     │  │   MinIO      │ │
│  │   (主数据库) │  │   (缓存)     │  │  (文件存储)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## 2. 项目目录结构

```
subway-wear-prediction/
│
├── backend/                      # 后端应用
│   ├── app/                     # 主应用目录
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI应用入口
│   │   ├── config.py           # 配置管理
│   │   │
│   │   ├── api/                # API端点
│   │   │   ├── __init__.py
│   │   │   ├── v1/            # API版本1
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py    # 认证相关API
│   │   │   │   ├── vehicles.py # 车辆管理API
│   │   │   │   ├── predictions.py # 预测API
│   │   │   │   ├── maintenance.py # 维护API
│   │   │   │   ├── reports.py  # 报表API
│   │   │   │   └── websocket.py # WebSocket端点
│   │   │   └── deps.py         # API依赖
│   │   │
│   │   ├── core/               # 核心功能
│   │   │   ├── __init__.py
│   │   │   ├── security.py    # 安全相关
│   │   │   ├── database.py    # 数据库配置
│   │   │   ├── redis_client.py # Redis配置
│   │   │   └── middleware.py   # 中间件
│   │   │
│   │   ├── models/             # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── vehicle.py     # 车辆模型
│   │   │   ├── wear.py        # 磨耗模型
│   │   │   ├── maintenance.py # 维护模型
│   │   │   └── user.py        # 用户模型
│   │   │
│   │   ├── schemas/            # Pydantic模式
│   │   │   ├── __init__.py
│   │   │   ├── vehicle.py
│   │   │   ├── wear.py
│   │   │   ├── prediction.py
│   │   │   ├── maintenance.py
│   │   │   └── user.py
│   │   │
│   │   ├── services/           # 业务服务
│   │   │   ├── __init__.py
│   │   │   ├── vehicle_service.py
│   │   │   ├── prediction_service.py
│   │   │   ├── maintenance_service.py
│   │   │   ├── report_service.py
│   │   │   └── notification_service.py
│   │   │
│   │   ├── ml/                 # 机器学习模块
│   │   │   ├── __init__.py
│   │   │   ├── models/        # 训练好的模型
│   │   │   ├── preprocessing.py # 数据预处理
│   │   │   ├── feature_engineering.py # 特征工程
│   │   │   ├── train.py       # 模型训练
│   │   │   ├── predict.py     # 预测逻辑
│   │   │   └── evaluate.py    # 模型评估
│   │   │
│   │   ├── utils/              # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── validators.py  # 数据验证
│   │   │   ├── formatters.py  # 数据格式化
│   │   │   ├── excel_handler.py # Excel处理
│   │   │   └── logger.py      # 日志工具
│   │   │
│   │   └── tasks/              # 异步任务
│   │       ├── __init__.py
│   │       ├── celery_app.py  # Celery配置
│   │       ├── scheduled.py   # 定时任务
│   │       └── background.py  # 后台任务
│   │
│   ├── alembic/                # 数据库迁移
│   │   ├── versions/
│   │   └── alembic.ini
│   │
│   ├── tests/                  # 测试文件
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_api/
│   │   ├── test_services/
│   │   └── test_ml/
│   │
│   ├── requirements.txt        # Python依赖
│   ├── requirements-dev.txt    # 开发依赖
│   ├── .env.example           # 环境变量示例
│   └── Dockerfile             # Docker配置
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── api/              # API调用
│   │   ├── components/       # 组件
│   │   ├── views/           # 页面
│   │   ├── store/           # 状态管理
│   │   ├── router/          # 路由
│   │   └── utils/           # 工具函数
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── docker/                    # Docker配置
│   ├── nginx/
│   │   └── nginx.conf
│   ├── postgres/
│   │   └── init.sql
│   └── redis/
│       └── redis.conf
│
├── scripts/                   # 脚本文件
│   ├── setup.sh             # 初始化脚本
│   ├── deploy.sh            # 部署脚本
│   └── backup.sh            # 备份脚本
│
├── docs/                      # 文档
│   ├── api/                 # API文档
│   ├── deployment/          # 部署文档
│   └── user_manual/         # 用户手册
│
├── k8s/                       # Kubernetes配置
│   ├── deployments/
│   ├── services/
│   └── configmaps/
│
├── .github/                   # GitHub Actions
│   └── workflows/
│       ├── test.yml
│       └── deploy.yml
│
├── docker-compose.yml         # Docker Compose配置
├── docker-compose.dev.yml     # 开发环境配置
├── .gitignore
├── README.md
├── PRD.md
└── ARCHITECTURE.md           # 本文档
```

## 3. 技术栈详细说明

### 3.1 后端技术栈

#### 核心框架
- **FastAPI**: 高性能异步Web框架
- **Python 3.9+**: 主要开发语言
- **Uvicorn**: ASGI服务器
- **Pydantic**: 数据验证和设置管理

#### 数据库
- **PostgreSQL 14+**: 主数据库
- **SQLAlchemy 2.0**: ORM框架
- **Alembic**: 数据库迁移工具
- **Redis 6+**: 缓存和会话存储

#### 机器学习
- **Scikit-learn**: 传统ML算法
- **XGBoost**: 梯度提升算法
- **TensorFlow/PyTorch**: 深度学习（可选）
- **Pandas**: 数据处理
- **NumPy**: 数值计算

#### 异步任务
- **Celery**: 分布式任务队列
- **RabbitMQ/Redis**: 消息队列

#### 认证授权
- **JWT**: JSON Web Token
- **OAuth2**: 授权框架
- **Passlib**: 密码哈希

#### 监控日志
- **Prometheus**: 指标收集
- **Grafana**: 可视化监控
- **ELK Stack**: 日志管理
- **Sentry**: 错误追踪

### 3.2 前端技术栈
- **Vue 3/React 17+**: 前端框架
- **TypeScript**: 类型安全
- **Tailwind CSS**: 样式框架
- **ECharts/D3.js**: 数据可视化
- **Axios**: HTTP客户端
- **Pinia/Redux**: 状态管理

### 3.3 部署技术栈
- **Docker**: 容器化
- **Kubernetes**: 容器编排
- **Nginx**: 反向代理
- **GitHub Actions**: CI/CD
- **MinIO**: 对象存储

## 4. API设计规范

### 4.1 RESTful API设计

```python
# API路由结构示例
/api/v1/
├── /auth
│   ├── POST   /login        # 用户登录
│   ├── POST   /logout       # 用户登出
│   └── POST   /refresh      # 刷新令牌
│
├── /vehicles
│   ├── GET    /             # 获取车辆列表
│   ├── POST   /             # 创建车辆
│   ├── GET    /{id}         # 获取车辆详情
│   ├── PUT    /{id}         # 更新车辆
│   └── DELETE /{id}         # 删除车辆
│
├── /wear-data
│   ├── GET    /             # 获取磨耗数据
│   ├── POST   /             # 录入磨耗数据
│   ├── POST   /import       # 批量导入
│   └── GET    /export       # 导出数据
│
├── /predictions
│   ├── POST   /single       # 单车预测
│   ├── POST   /batch        # 批量预测
│   ├── GET    /history      # 历史预测
│   └── GET    /trends       # 趋势分析
│
├── /maintenance
│   ├── GET    /plans        # 维护计划
│   ├── POST   /plans        # 创建计划
│   ├── PUT    /plans/{id}   # 更新计划
│   └── GET    /suggestions  # 维护建议
│
└── /reports
    ├── GET    /dashboard    # 仪表板数据
    ├── GET    /statistics   # 统计数据
    ├── POST   /generate     # 生成报表
    └── GET    /download/{id} # 下载报表
```

### 4.2 WebSocket实时通信

```python
# WebSocket端点
/ws/
├── /notifications  # 实时通知
├── /monitoring    # 实时监控
└── /updates      # 数据更新
```

## 5. 数据库设计

### 5.1 主要数据表

```sql
-- 车辆表
CREATE TABLE vehicles (
    id UUID PRIMARY KEY,
    vehicle_code VARCHAR(50) UNIQUE NOT NULL,
    model VARCHAR(100),
    line_number VARCHAR(50),
    manufacture_date DATE,
    commissioning_date DATE,
    total_mileage DECIMAL(10,2),
    status VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 磨耗测量表
CREATE TABLE wear_measurements (
    id UUID PRIMARY KEY,
    vehicle_id UUID REFERENCES vehicles(id),
    measurement_date TIMESTAMP,
    mileage_at_measurement DECIMAL(10,2),
    measurement_type VARCHAR(50),
    component_type VARCHAR(50),
    component_position VARCHAR(50),
    wear_value DECIMAL(10,4),
    thickness DECIMAL(10,4),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP
);

-- 预测记录表
CREATE TABLE predictions (
    id UUID PRIMARY KEY,
    vehicle_id UUID REFERENCES vehicles(id),
    prediction_date TIMESTAMP,
    component_type VARCHAR(50),
    current_wear DECIMAL(10,4),
    predicted_wear DECIMAL(10,4),
    remaining_life_days INTEGER,
    remaining_life_mileage DECIMAL(10,2),
    confidence_score DECIMAL(5,4),
    risk_level VARCHAR(20),
    created_at TIMESTAMP
);

-- 维护计划表
CREATE TABLE maintenance_plans (
    id UUID PRIMARY KEY,
    vehicle_id UUID REFERENCES vehicles(id),
    plan_date DATE,
    plan_type VARCHAR(50),
    priority VARCHAR(20),
    component_type VARCHAR(50),
    action_required TEXT,
    estimated_cost DECIMAL(10,2),
    estimated_downtime_hours INTEGER,
    status VARCHAR(20),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    full_name VARCHAR(255),
    role VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP,
    last_login TIMESTAMP
);
```

## 6. 安全架构

### 6.1 认证授权流程
```python
# JWT认证流程
1. 用户登录 -> 验证凭据
2. 生成JWT令牌 (access_token + refresh_token)
3. 客户端存储令牌
4. 请求携带Bearer Token
5. 服务端验证令牌
6. 令牌过期后使用refresh_token刷新
```

### 6.2 安全措施
- HTTPS/TLS加密传输
- SQL注入防护（参数化查询）
- XSS防护（输入验证和输出编码）
- CSRF防护（CSRF令牌）
- 速率限制（防DDoS）
- 敏感数据加密存储
- 审计日志记录

## 7. 性能优化策略

### 7.1 缓存策略
- Redis缓存热点数据
- 多级缓存架构
- 缓存预热机制
- 缓存失效策略

### 7.2 数据库优化
- 索引优化
- 查询优化
- 分区表设计
- 读写分离

### 7.3 异步处理
- 异步API端点
- 后台任务队列
- 批处理优化
- 并发控制

## 8. 部署架构

### 8.1 容器化部署
```yaml
# docker-compose.yml示例
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/subway
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=subway
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf
```

### 8.2 Kubernetes部署
- Deployment配置
- Service暴露
- Ingress路由
- ConfigMap/Secret管理
- HPA自动伸缩

## 9. 监控告警

### 9.1 监控指标
- API响应时间
- 请求成功率
- 系统资源使用
- 数据库性能
- 预测准确率

### 9.2 告警规则
- 系统异常告警
- 性能降级告警
- 安全事件告警
- 业务异常告警

## 10. 开发规范

### 10.1 代码规范
- PEP 8 Python代码规范
- Type Hints类型注解
- Docstring文档字符串
- 单元测试覆盖率>80%

### 10.2 Git工作流
- Git Flow分支模型
- Commit规范（Conventional Commits）
- Code Review流程
- CI/CD集成

## 11. 扩展性设计

### 11.1 微服务拆分
- 认证服务
- 车辆管理服务
- 预测服务
- 报表服务
- 通知服务

### 11.2 插件化架构
- 预测算法插件
- 数据源插件
- 报表模板插件
- 通知渠道插件

## 12. 灾备方案

### 12.1 数据备份
- 定期全量备份
- 实时增量备份
- 异地容灾备份

### 12.2 高可用设计
- 服务多实例部署
- 数据库主从复制
- 负载均衡
- 故障自动切换

---

本架构设计旨在构建一个高性能、可扩展、易维护的地铁车辆磨耗预测系统。随着项目发展，架构将持续优化和演进。