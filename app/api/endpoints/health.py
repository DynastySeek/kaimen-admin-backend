"""
健康检查API端点
"""
import time
from datetime import datetime
from fastapi import APIRouter

from app.utils.response import success_response
from app.constants.response_codes import ResponseCode

router = APIRouter()


@router.get("/health", summary="健康检查")
def health_check():
    """
    健康检查接口
    
    Returns:
        dict: 包含服务状态、时间戳等信息的响应
    """
    current_time = datetime.now()
    
    health_data = {
        "status": ResponseCode.SUCCESS,
        "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "service": "kaimen-admin-backend",
        "version": "1.0.0"
    }
    
    return success_response(
        data=health_data,
        message="服务运行正常"
    )

