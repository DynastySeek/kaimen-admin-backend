"""
认证相关API端点
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session

from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.user import UserInfo
from app.services.auth import authenticate_user, create_access_token
from app.utils.response import success_response, error_response
from app.constants.response_codes import ResponseCode
from app.utils.db import get_session
from app.config.settings import ACCESS_TOKEN_EXPIRE_SECONDS

router = APIRouter()


@router.post("/login", summary="用户登录")
def login(request: LoginRequest, session: Session = Depends(get_session)):
    user = authenticate_user(request.username, request.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(ResponseCode.FAILURE, "用户名或密码错误")
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return success_response(
        data={
            "access_token": access_token,
            "expires_in": ACCESS_TOKEN_EXPIRE_SECONDS,
        },
        message="登录成功"
    )