"""
认证相关API端点
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session

from ...schemas.auth import LoginRequest, LoginResponse, UserInfo
from ...services.auth_service import authenticate_user, create_access_token, get_current_user
from ...config.database import get_session
from ...models.user import User

router = APIRouter()


@router.post("/login", response_model=LoginResponse, summary="用户登录")
def login(request: LoginRequest, session: Session = Depends(get_session)):
    """
    用户登录接口
    
    Args:
        request: 登录请求数据
        session: 数据库会话
        
    Returns:
        LoginResponse: 登录响应
        
    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    # 验证用户
    user = authenticate_user(session, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 创建访问令牌
    access_token = create_access_token(data={"sub": user.name})
    
    # 返回登录响应
    return LoginResponse(
        code=200,
        message="登录成功",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 7200,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "nickname": user.nickname,
                "phone": user.phone,
                "avatar": user.avatar
            }
        }
    )


@router.get("/user/info", summary="获取用户信息")
def get_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息
    
    Args:
        current_user: 当前用户
        
    Returns:
        dict: 用户信息响应
    """
    return {
        "code": 200,
        "message": "获取用户信息成功",
        "data": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role,
            "nickname": current_user.nickname,
            "phone": current_user.phone,
            "avatar": current_user.avatar
        }
    }