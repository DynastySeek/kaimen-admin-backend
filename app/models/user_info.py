"""
用户信息数据模型
"""
from sqlmodel import SQLModel, Field, Column, String
from typing import Optional
from datetime import datetime


class UserInfo(SQLModel, table=True):
    """用户信息模型"""
    __tablename__ = "userinfo"

    id: str = Field(sa_column=Column("_id", String(34), primary_key=True))
    phone: Optional[str] = None
    created_at: Optional[datetime] = Field(default=None, sa_column=Column("created_at"))
    nick_name: Optional[str] = None