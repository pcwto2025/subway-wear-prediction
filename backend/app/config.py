"""
应用配置管理
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    APP_NAME: str = "Subway Wear Prediction System"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True

    # API配置
    API_V1_PREFIX: str = "/api/v1"

    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/subway_wear"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_CACHE_TTL: int = 3600  # 缓存过期时间（秒）

    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]

    # 允许的主机
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIRECTORY: str = "./uploads"
    ALLOWED_EXTENSIONS: List[str] = [".xlsx", ".xls", ".csv"]

    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # ML模型配置
    MODEL_PATH: str = "./app/ml/models"
    MODEL_VERSION: str = "v1.0"
    PREDICTION_CONFIDENCE_THRESHOLD: float = 0.85

    # 邮件配置
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "noreply@subway-wear.com"

    # Sentry配置（错误追踪）
    SENTRY_DSN: Optional[str] = None

    # 限流配置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # 秒

    # 业务配置
    WEAR_THRESHOLDS: dict = {
        "wheelset": {
            "min_diameter": 840,  # mm
            "max_flang_wear": 32,  # mm
            "critical_tread_wear": 8,  # mm
        },
        "brake_pad": {
            "min_thickness": 10,  # mm
        },
        "pantograph": {
            "min_thickness": 5,  # mm
        }
    }

    RISK_LEVELS: dict = {
        "critical": {"color": "#FF0000", "days": 7},
        "high": {"color": "#FF6600", "days": 30},
        "medium": {"color": "#FFB800", "days": 60},
        "low": {"color": "#66CC00", "days": 90},
        "minimal": {"color": "#00CC00", "days": 180}
    }

    MAINTENANCE_PRIORITIES: List[str] = ["urgent", "high", "medium", "low"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings():
    """获取配置单例"""
    return Settings()


# 导出配置实例
settings = get_settings()