"""
认证服务
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.models.user import User
from app.config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_SECONDS
from app.utils.db import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_SECONDS) -> str:
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间（秒）
        
    Returns:
        str: JWT令牌
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌
        
    Returns:
        Optional[str]: 用户ID或None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    用户认证
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        Optional[User]: 用户对象或None
    """
    with Session(get_session().__next__()) as session:
        statement = select(User).where(User.name == username)
        user = session.exec(statement).first()
        
        if not user:
            return None
        
        # 直接比较明文密码
        if user.password != password:
            return None
        
        return user