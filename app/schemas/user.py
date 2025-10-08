"""
用户相关 Schema
"""
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator
from .base import BaseResponseSchema
from ..constants.enums import UserStatus, UserRole, Gender


class UserCreateSchema(BaseModel):
    """用户创建 Schema"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    password: str = Field(..., min_length=8, max_length=128, description="密码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    gender: Optional[Gender] = Field(None, description="性别")
    
    @validator('password')
    def validate_password(cls, v):
        """密码验证"""
        if len(v) < 8:
            raise ValueError('密码长度不能少于8位')
        return v


class UserUpdateSchema(BaseModel):
    """用户更新 Schema"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[Gender] = Field(None, description="性别")
    birthday: Optional[str] = Field(None, max_length=10, description="生日")


class UserPasswordUpdateSchema(BaseModel):
    """用户密码更新 Schema"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """新密码验证"""
        if len(v) < 8:
            raise ValueError('密码长度不能少于8位')
        return v


class UserResponseSchema(BaseResponseSchema):
    """用户响应 Schema"""
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    gender: Optional[Gender] = Field(None, description="性别")
    birthday: Optional[str] = Field(None, description="生日")
    status: UserStatus = Field(..., description="用户状态")
    role: UserRole = Field(..., description="用户角色")
    is_email_verified: bool = Field(..., description="邮箱是否验证")
    is_phone_verified: bool = Field(..., description="手机是否验证")


class UserLoginSchema(BaseModel):
    """用户登录 Schema"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class UserLoginResponseSchema(BaseModel):
    """用户登录响应 Schema"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user: UserResponseSchema = Field(..., description="用户信息")


class UserListQuerySchema(BaseModel):
    """用户列表查询 Schema"""
    username: Optional[str] = Field(None, description="用户名搜索")
    email: Optional[str] = Field(None, description="邮箱搜索")
    status: Optional[UserStatus] = Field(None, description="用户状态筛选")
    role: Optional[UserRole] = Field(None, description="用户角色筛选")