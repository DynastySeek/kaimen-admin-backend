"""
用户服务
"""
from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from app.models.user import User
from app.utils.db import get_session
from app.services.auth import verify_token
from app.utils.response import ResponseCode

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_user_by_id(user_id: int) -> Optional[User]:
    """
    根据用户ID获取用户
    
    Args:
        user_id: 用户ID
        
    Returns:
        Optional[User]: 用户对象或None
    """
    with Session(get_session().__next__()) as session:
        statement = select(User).where(User.id == user_id)
        return session.exec(statement).first()


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    获取当前用户
    
    Args:
        token: JWT令牌
        
    Returns:
        User: 当前用户
        
    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "code": ResponseCode.UNAUTHORIZED,
            "message": "认证失败",
            "data": None
        },
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id = verify_token(token)
    if user_id is None:
        raise credentials_exception
    
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise credentials_exception
    
    user = get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user