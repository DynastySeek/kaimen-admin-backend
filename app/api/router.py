"""
API 路由配置
"""
from fastapi import APIRouter

from .endpoints import auth

# 创建主路由
api_router = APIRouter()

# 注册认证相关路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])