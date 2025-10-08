"""
用户相关API端点
"""
from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user_required
from app.models.user import User
from app.utils.response import success_response

router = APIRouter()


@router.get("/info", summary="获取用户信息")
def get_user_info(current_user: User = Depends(get_current_user_required)):
    """
    获取当前用户信息
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        dict: 用户信息响应
    """
    return success_response(
        data={
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role,
            "nickname": current_user.nickname,
            "phone": current_user.phone,
            "avatar": current_user.avatar
        },
        message="获取用户信息成功"
    )