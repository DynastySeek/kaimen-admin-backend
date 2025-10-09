from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class UserInfo(BaseModel):
    """用户信息基础模型"""
    id: int = Field(..., description="用户ID")
    name: str = Field(..., description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    role: str = Field(default="user", description="角色")
    nickname: Optional[str] = Field(None, description="昵称")
    phone: Optional[str] = Field(None, description="手机号")
    avatar: Optional[str] = Field(None, description="头像")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")


class UserListRequest(BaseModel):
    """用户列表查询请求"""
    page: int = Field(1, ge=1, description="页码")
    pageSize: int = Field(20, ge=1, le=100, description="每页数量")
    id: Optional[int] = Field(None, description="用户ID")
    name: Optional[str] = Field(None, description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    phone: Optional[str] = Field(None, description="手机号")


class UserListResponse(BaseModel):
    """用户列表响应"""
    list: List[UserInfo] = Field(..., description="用户列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    pageSize: int = Field(..., description="每页数量")


class UserCreateRequest(BaseModel):
    """创建用户请求"""
    name: str = Field(..., min_length=1, max_length=50, description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    role: Optional[str] = Field("user", description="角色")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    phone: Optional[str] = Field(None, description="手机号")
    avatar: Optional[str] = Field(None, description="头像")


class UserUpdateSelfRequest(BaseModel):
    """用户更新自己信息请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="用户名")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="密码")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    avatar: Optional[str] = Field(None, description="头像")


class UserUpdateAdminRequest(BaseModel):
    """管理员更新用户信息请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="密码")
    role: Optional[str] = Field(None, description="角色")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    phone: Optional[str] = Field(None, description="手机号")
    avatar: Optional[str] = Field(None, description="头像")