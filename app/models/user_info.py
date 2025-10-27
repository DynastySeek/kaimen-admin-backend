"""
用户信息数据模型
"""
from sqlmodel import SQLModel, Field, Column, String
from typing import Optional
from app.config.settings import get_table_suffix


class UserInfo(SQLModel, table=True):
    """用户信息模型"""
    __tablename__ = f"userinfo{get_table_suffix('userinfo')}"

    id: str = Field(sa_column_kwargs={"name": "_id"}, primary_key=True)
    phone: Optional[str] = None
    created_at: Optional[int] = Field(default=None, sa_column=Column("createdAt"))
    nick_name: Optional[str] = None