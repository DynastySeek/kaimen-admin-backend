"""
API 路由配置
"""
from fastapi import APIRouter

from app.api.endpoints import auth, user, appraisal, health

# 创建主路由
api_router = APIRouter()

# 注册健康检查路由
api_router.include_router(health.router, tags=["健康检查"])

# 注册认证相关路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 注册用户相关路由
api_router.include_router(user.router, prefix="/user", tags=["用户"])

# 注册鉴定相关路由
api_router.include_router(appraisal.router, prefix="/appraisal", tags=["鉴定"])