"""
主路由汇总模块
"""
from fastapi import APIRouter
from .endpoints import auth

# 创建主路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["认证"]
)