"""
依赖注入模块
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.auth import verify_token
from app.services.user import get_user_by_id
from app.models.user import User
from app.constants.response_codes import ResponseCode

# HTTP Bearer 认证方案
security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    获取当前用户（可选）
    
    Args:
        credentials: HTTP认证凭据
        
    Returns:
        Optional[User]: 用户对象或None
    """
    if not credentials:
        return None
    
    user_id = verify_token(credentials.credentials)
    if not user_id:
        return None
    
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return None
    
    return get_user_by_id(user_id)


async def get_current_user_required(
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    """
    获取当前用户（必需）
    
    Args:
        current_user: 当前用户（可选）
        
    Returns:
        User: 用户对象
        
    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": ResponseCode.UNAUTHORIZED,
                "message": "认证失败，请先登录",
                "data": None
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_user_required)
) -> User:
    """
    获取管理员用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 管理员用户对象
        
    Raises:
        HTTPException: 权限不足时抛出403错误
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": ResponseCode.FORBIDDEN,
                "message": "权限不足，需要管理员权限",
                "data": None
            }
        )
    
    return current_user