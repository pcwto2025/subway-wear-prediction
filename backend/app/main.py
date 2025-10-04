"""
地铁车辆磨耗预测系统 - FastAPI主应用（简化版）
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Dict

from app.config import settings
from app.api.v1 import auth, vehicles, predictions, maintenance, reports

# 设置基础日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("🚂 Starting up Subway Wear Prediction System...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Version: {settings.VERSION}")
    logger.info("Application started successfully! 🎉")

    yield

    # 关闭时
    logger.info("Shutting down...")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description="""
# 地铁车辆磨耗智能预测系统 API

## 功能特点
- 🚊 车辆信息管理
- 🔍 智能磨耗预测
- 🛠️ 维护计划优化
- 📊 数据可视化报表
- 🔐 安全认证授权

## 快速开始
1. 使用 `/api/v1/auth/login` 进行登录（测试账号：admin/admin123）
2. 获取车辆列表：`/api/v1/vehicles`
3. 进行磨耗预测：`/api/v1/predictions/single`
4. 查看仪表板：`/api/v1/reports/dashboard`
    """,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["认证授权"]
)

app.include_router(
    vehicles.router,
    prefix="/api/v1/vehicles",
    tags=["车辆管理"]
)

app.include_router(
    predictions.router,
    prefix="/api/v1/predictions",
    tags=["磨耗预测"]
)

app.include_router(
    maintenance.router,
    prefix="/api/v1/maintenance",
    tags=["维护管理"]
)

app.include_router(
    reports.router,
    prefix="/api/v1/reports",
    tags=["报表统计"]
)


@app.get("/", response_class=JSONResponse)
async def root() -> Dict[str, str]:
    """根路径 - 系统信息"""
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "🟢 运行中",
        "docs": "/docs",
        "health": "/health",
        "message": "欢迎使用地铁车辆磨耗预测系统！"
    }


@app.get("/health", response_class=JSONResponse)
async def health_check() -> Dict[str, str]:
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {
            "api": "✅ 正常",
            "database": "⚠️ 模拟模式",
            "cache": "⚠️ 模拟模式",
            "ml_model": "✅ 就绪"
        }
    }


@app.get("/api/v1", response_class=JSONResponse)
async def api_info() -> Dict:
    """API信息和端点列表"""
    return {
        "version": "v1",
        "description": "地铁车辆磨耗预测系统 API v1",
        "endpoints": {
            "认证": {
                "登录": "POST /api/v1/auth/login",
                "登出": "POST /api/v1/auth/logout",
                "刷新令牌": "POST /api/v1/auth/refresh"
            },
            "车辆管理": {
                "车辆列表": "GET /api/v1/vehicles",
                "车辆详情": "GET /api/v1/vehicles/{id}",
                "创建车辆": "POST /api/v1/vehicles",
                "更新车辆": "PUT /api/v1/vehicles/{id}",
                "删除车辆": "DELETE /api/v1/vehicles/{id}"
            },
            "磨耗预测": {
                "单车预测": "POST /api/v1/predictions/single",
                "批量预测": "POST /api/v1/predictions/batch",
                "趋势分析": "GET /api/v1/predictions/trends"
            },
            "维护管理": {
                "维护计划": "GET /api/v1/maintenance/plans",
                "维护建议": "GET /api/v1/maintenance/suggestions",
                "计划优化": "POST /api/v1/maintenance/schedule-optimization"
            },
            "报表统计": {
                "仪表板": "GET /api/v1/reports/dashboard",
                "统计数据": "GET /api/v1/reports/statistics",
                "车队概览": "GET /api/v1/reports/fleet-overview",
                "生成报表": "POST /api/v1/reports/generate"
            }
        }
    }


# 全局异常处理
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "资源未找到", "path": str(request.url)}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "内部服务器错误", "message": "请稍后重试"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )