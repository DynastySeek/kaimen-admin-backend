"""
健康检查API端点
"""
from fastapi import APIRouter
from app.utils.response import success_response

router = APIRouter()


@router.get("/health", summary="健康检查")
def health_check():
    """
    健康检查接口
    
    返回服务基本信息，用于监控服务状态
    """
    return success_response(
        data={
            "name": "开门寻宝管理后台服务",
            "version": "1.0.0",
            "status": "healthy",
            "description": "基于 FastAPI 构建的管理后台系统"
        },
        message="服务运行正常"
    )