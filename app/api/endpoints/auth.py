"""
认证相关API端点
"""
from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import LoginRequest, LoginResponse, UserInfo
from app.services.auth import authenticate_user, create_access_token
from app.utils.response import success_response, error_response, ResponseCode

router = APIRouter()


@router.post("/login", summary="用户登录")
def login(request: LoginRequest):
    """
    用户登录接口
    """
    # 验证用户
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_response(ResponseCode.UNAUTHORIZED, "用户名或密码错误")
        )
    
    # 创建访问令牌
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # 返回登录响应
    return success_response(
        data={
            "access_token": access_token,
            "expires_in": 86400
        },
        message="登录成功"
    )