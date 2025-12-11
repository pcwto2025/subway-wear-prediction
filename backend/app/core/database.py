"""数据库配置和连接管理"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://subway_user:subway_pass@localhost:5432/subway_wear_db"
)
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "False").lower() == "true"
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "20"))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "40"))

# 根据数据库类型选择合适的驱动
if DATABASE_URL.startswith("sqlite"):
    # 对于SQLite，使用aiosqlite作为异步驱动
    if not DATABASE_URL.startswith("sqlite+aiosqlite"):
        DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
    engine = create_async_engine(
        DATABASE_URL,
        echo=DATABASE_ECHO,
        # SQLite不支持连接池参数，所以不使用这些参数
        connect_args={"check_same_thread": False}
    )
else:
    # 对于PostgreSQL等其他数据库，使用原始配置
    engine = create_async_engine(
        DATABASE_URL,
        echo=DATABASE_ECHO,
        pool_size=DATABASE_POOL_SIZE,
        max_overflow=DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,
    )

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 创建基础模型类
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的依赖函数"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库表"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()


async def check_database_health() -> dict:
    """检查数据库连接健康状态"""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute("SELECT 1")
            return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}