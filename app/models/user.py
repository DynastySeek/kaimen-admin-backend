"""
用户相关数据模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone


class User(SQLModel, table=True):
    """
    用户模型
    """
    __tablename__ = "user"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(description="用户名")
    email: Optional[str] = Field(default=None, description="邮箱")
    password: str = Field(description="密码")
    role: Optional[str] = Field(default="user", description="角色")
    nickname: Optional[str] = Field(default=None, description="昵称")
    phone: Optional[str] = Field(default=None, description="手机号")
    avatar: Optional[str] = Field(default=None, description="头像")
    create_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="创建时间"
    )
    update_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="更新时间"
    )