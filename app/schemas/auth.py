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


class UserInfo(BaseModel):
    """
    用户信息模式
    """
    id: int = Field(..., description="用户ID")
    name: str = Field(..., description="用户名")
    email: str = Field(None, description="邮箱")
    role: str = Field(default="user", description="角色")
    nickname: str = Field(None, description="昵称")
    phone: str = Field(None, description="手机号")
    avatar: str = Field(None, description="头像")