"""认证相关API"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """用户登录"""
    # 模拟登录（实际需要验证密码）
    if request.username == "admin" and request.password == "admin123":
        return LoginResponse(
            access_token="mock-jwt-token",
            user_id="user-123",
            username=request.username
        )
    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/logout")
async def logout():
    """用户登出"""
    return {"message": "Logged out successfully"}


@router.post("/refresh")
async def refresh_token():
    """刷新令牌"""
    return {
        "access_token": "new-mock-jwt-token",
        "token_type": "bearer"
    }