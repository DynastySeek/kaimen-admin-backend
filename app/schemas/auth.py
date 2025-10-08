"""
认证相关数据模式
"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """
    登录请求模式
    """
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class LoginResponse(BaseModel):
    """
    登录响应模式
    """
    code: int = Field(default=200, description="响应码")
    message: str = Field(default="登录成功", description="响应消息")
    data: dict = Field(..., description="响应数据")