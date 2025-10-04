# 地铁车辆磨耗预测系统
# Subway Vehicle Wear Prediction System

一个基于FastAPI和Vue.js的地铁车辆磨耗智能预测系统，通过机器学习算法预测车辆关键部件的磨耗状态，优化维护计划。

## 🚀 功能特点

- **🚊 车辆信息管理** - 完整的车辆信息录入和管理
- **🔍 智能磨耗预测** - 基于历史数据的磨耗预测算法
- **🛠️ 维护计划优化** - 自动生成优化的维护建议
- **📊 数据可视化** - 直观的图表和仪表板
- **🔐 安全认证** - JWT Token认证授权

## 📁 项目结构

```
subway-wear-prediction/
├── backend/               # FastAPI后端
│   ├── app/              # 应用代码
│   │   ├── api/          # API端点
│   │   ├── core/         # 核心功能
│   │   ├── models/       # 数据模型
│   │   └── services/     # 业务服务
│   └── requirements.txt   # Python依赖
├── frontend/              # Vue.js前端
│   ├── src/              # 源代码
│   │   ├── api/          # API调用
│   │   ├── components/   # 组件
│   │   ├── views/        # 页面
│   │   └── router/       # 路由
│   └── package.json       # Node依赖
├── PRD.md                # 产品需求文档
└── ARCHITECTURE.md        # 架构设计文档
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
- PostgreSQL 14+ (可选)
- Redis 6+ (可选)

### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

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

访问 http://localhost:3000 查看前端界面

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

## 📖 文档

- [产品需求文档](PRD.md)
- [架构设计文档](ARCHITECTURE.md)
- [API文档](http://localhost:8000/docs)

## 🤝 贡献

欢迎提交Issue和Pull Request

## 📄 许可证

MIT License

## 👥 团队

地铁车辆磨耗预测系统开发团队

---

**版本**: v1.0.0
**更新日期**: 2024-01-26