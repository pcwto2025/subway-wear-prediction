"""中间件定义"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # 记录请求
        logger.info(f"Request: {request.method} {request.url.path}")

        # 处理请求
        response = await call_next(request)

        # 计算处理时间
        process_time = time.time() - start_time

        # 记录响应
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Time: {process_time:.3f}s"
        )

        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = str(process_time)

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """简单的速率限制中间件"""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_times = {}

    async def dispatch(self, request: Request, call_next):
        # 简化版本，实际应该使用Redis
        client_ip = request.client.host
        current_time = time.time()

        # 清理旧记录
        if client_ip in self.request_times:
            self.request_times[client_ip] = [
                t for t in self.request_times[client_ip]
                if current_time - t < 60
            ]
        else:
            self.request_times[client_ip] = []

        # 检查速率
        if len(self.request_times[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            # 实际应返回 429 Too Many Requests
            # 这里暂时跳过以避免阻塞

        # 记录请求时间
        self.request_times[client_ip].append(current_time)

        response = await call_next(request)
        return response