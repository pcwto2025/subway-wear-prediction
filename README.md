# 地铁车辆磨耗预测系统 (MMM-SL)
# Subway Vehicle Wear Prediction System (MMM-SL)

[![Version](https://img.shields.io/badge/version-v1.1.0-blue)](https://github.com/pcwto2025/subway-wear-prediction)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-yellow)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/vue-3.0+-brightgreen)](https://vuejs.org/)

一个专为MMM-SL地铁项目设计的智能车辆磨耗预测系统，支持16列列车的全生命周期管理，通过机器学习算法预测关键部件磨耗状态，优化维护计划。

## 🚀 核心功能

### 🚇 MMM-SL车辆管理系统
- **项目代码**: MMM-SL
- **列车编号**: Tr01-Tr16 (16列列车)
- **车厢编组**: 12编组标准配置 (SL前缀编号)
- **特种车辆**: 支持特种维护车辆管理

### 🌍 国际化支持
- **多语言**: 中文(zh-CN)、英文(en-US)
- **动态切换**: 实时语言切换，无需刷新
- **完整覆盖**: UI、验证消息、日期格式全面国际化

### 👤 用户管理系统
- **认证授权**: JWT Token安全认证
- **角色管理**: 管理员、操作员、查看者多角色
- **权限控制**: 细粒度API访问控制
- **会话管理**: 自动续期与安全退出

### 🗄️ 数据库配置
- **PostgreSQL**: 主数据库，支持复杂查询
- **Redis**: 缓存层（可选）
- **数据初始化**: 自动建表与示例数据
- **连接池**: 高并发性能优化

### 📊 高级功能
- **智能预测**: 基于历史数据的磨耗预测
- **维护优化**: 自动生成维护建议
- **实时监控**: 车辆状态实时跟踪
- **数据分析**: 多维度统计报表

## 📁 项目结构

```
subway-wear-prediction/
├── backend/                    # FastAPI后端
│   ├── app/                   # 应用代码
│   │   ├── api/               # API端点
│   │   │   └── v1/           # API v1版本
│   │   │       └── endpoints/ # 端点实现
│   │   ├── core/             # 核心功能
│   │   │   ├── auth.py      # 认证模块
│   │   │   └── database.py  # 数据库配置
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # Pydantic模式
│   │   └── services/         # 业务服务
│   └── requirements.txt       # Python依赖
├── frontend/                   # Vue.js前端
│   ├── src/                   # 源代码
│   │   ├── api/              # API调用
│   │   ├── components/       # Vue组件
│   │   │   └── VehicleFormDialog.vue
│   │   ├── composables/      # 组合式API
│   │   ├── i18n/             # 国际化配置
│   │   │   └── locales/      # 语言文件
│   │   ├── types/            # TypeScript类型
│   │   └── views/            # 页面视图
│   │       └── VehicleManagement.vue
│   └── package.json           # Node依赖
├── database/                   # 数据库脚本
│   └── init.sql              # 初始化脚本
├── docker-compose.yml          # Docker编排
├── .env.example               # 环境变量示例
├── PRD.md                     # 产品需求文档
└── ARCHITECTURE.md            # 架构设计文档
```

## 🛠️ 技术栈

### 后端
- **FastAPI** - 高性能异步Web框架
- **Python 3.9+** - 主要开发语言
- **SQLAlchemy** - ORM框架
- **PostgreSQL** - 主数据库
- **Redis** - 缓存和会话

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全
- **Element Plus** - UI组件库
- **ECharts** - 数据可视化
- **Tailwind CSS** - 原子化CSS框架

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- PostgreSQL 14+
- Redis 6+ (可选，暂未启用)
- uv (Python包管理器)

### 数据库初始化

```bash
# 启动PostgreSQL服务
pg_ctl -D $PREFIX/var/lib/postgresql start

# 创建数据库用户和数据库
createuser -s subway_user
createdb -O subway_user subway_wear_db

# 设置密码并初始化数据
PGPASSWORD=subway_pass psql -U subway_user -d subway_wear_db -f database/init.sql

# 验证数据库
PGPASSWORD=subway_pass psql -U subway_user -d subway_wear_db -c "\dt"
```

### 后端启动

```bash
# 进入后端目录
cd backend

# 使用uv安装依赖
uv pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件设置数据库连接

# 启动服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看API文档

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:3001 查看前端界面

## 📝 默认登录

- 用户名: `admin`
- 密码: `admin123`

## 📊 主要功能

### 1. 仪表板
- 车队状态总览
- 风险等级分布
- 即将维护列表
- 实时告警信息

### 2. 车辆管理
- 车辆信息录入
- 运营数据记录
- 维护历史管理

### 3. 磨耗预测
- 单车预测分析
- 批量预测处理
- 趋势分析图表
- 剩余寿命预测

### 4. 维护管理
- 维护计划制定
- 优先级排序
- 成本优化分析
- 计划执行跟踪

### 5. 报表统计
- 月度/季度/年度报表
- 自定义数据导出
- 性能指标分析

## 📈 预测算法

系统采用多种算法进行磨耗预测：

- **线性回归** - 基础趋势预测
- **时间序列分析** - 季节性模式识别
- **机器学习模型** - 复杂模式识别
- **环境因素修正** - 温度、湿度、载客率影响

## 🔐 安全特性

- JWT Token认证
- 密码加密存储
- API访问控制
- 请求速率限制
- CORS配置

## 🌍 部署

### Docker部署

```bash
# 构建镜像
docker build -t subway-wear-prediction .

# 运行容器
docker run -p 8000:8000 -p 3000:3000 subway-wear-prediction
```

### 生产环境

参考 `ARCHITECTURE.md` 中的部署架构章节

## 📖 API端点

### 用户管理
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/register` - 用户注册
- `GET /api/v1/users/me` - 获取当前用户信息
- `GET /api/v1/users/` - 获取用户列表（管理员）
- `PUT /api/v1/users/{user_id}` - 更新用户信息
- `DELETE /api/v1/users/{user_id}` - 删除用户

### 车辆管理
- `GET /api/v1/vehicles/` - 获取车辆列表
- `POST /api/v1/vehicles/` - 创建新车辆
- `GET /api/v1/vehicles/{vehicle_id}` - 获取车辆详情
- `PUT /api/v1/vehicles/{vehicle_id}` - 更新车辆信息
- `DELETE /api/v1/vehicles/{vehicle_id}` - 删除车辆
- `POST /api/v1/vehicles/batch` - 批量操作车辆

### 磨耗预测
- `POST /api/v1/prediction/single` - 单车预测
- `POST /api/v1/prediction/batch` - 批量预测
- `GET /api/v1/prediction/history` - 预测历史

## 🌍 国际化支持

系统支持中英文双语切换：
- 中文（zh-CN）：默认语言
- 英文（en-US）：完整英文界面

切换方式：
1. 点击页面右上角语言切换按钮
2. 语言设置会自动保存到本地

## 🔐 安全特性

- JWT Token认证
- 密码加密存储（bcrypt）
- API访问控制（基于角色）
- 请求速率限制
- CORS配置
- SQL注入防护

## 🤝 贡献

欢迎提交Issue和Pull Request

## 📄 许可证

MIT License

## 👥 团队

地铁车辆磨耗预测系统开发团队

---

**版本**: v1.1.0
**更新日期**: 2024-01-26

## 📋 更新日志

### v1.1.0 (2024-01-26)
- ✨ 新增MMM-SL车辆管理系统，支持16列列车管理
- 🌍 实现完整的国际化支持（中文/英文）
- 👤 添加用户认证与管理API
- 🗄️ 集成PostgreSQL数据库与初始化脚本
- 🚗 实现12编组车厢自动编号生成
- 🔧 添加特种维护车辆管理接口
- 📦 迁移至uv包管理器
- 🔐 实现JWT Token认证机制

### v1.0.0 (2024-01-25)
- 🎉 初始版本发布
- 📊 基础磨耗预测功能
- 📈 数据可视化仪表板