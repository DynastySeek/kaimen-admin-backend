"""
鉴定相关的数据模型
"""
from sqlmodel import SQLModel, Field, Relationship, Column, String, JSON
from typing import Optional, List
from datetime import datetime, timezone
from app.config.settings import get_table_suffix


class Appraisal(SQLModel, table=True):
    """鉴定订单模型"""
    __tablename__ = f"appraisal{get_table_suffix('appraisal')}"

    id: str = Field(sa_column=Column("_id", String(34), primary_key=True))
    title: Optional[str] = None
    desc: Optional[str] = Field(default=None, sa_column=Column("desc", String(255)))
    appraisal_status: Optional[str] = None
    first_class: Optional[str] = None
    created_at: Optional[int] = Field(default=None, sa_column=Column("createdAt"))
    updated_at: Optional[int] = Field(default=None, sa_column=Column("updatedAt"))
    userinfo_id: Optional[str] = Field(default=None, sa_column=Column("userinfo_id", String(64)))

    resources: List["AppraisalResource"] = Relationship(back_populates="appraisal")


class AppraisalResource(SQLModel, table=True):
    """鉴定资源模型"""
    __tablename__ = f"appraisal_resource{get_table_suffix('appraisal_resource')}"

    id: str = Field(sa_column=Column("_id", String(34), primary_key=True))
    appraisal_id: Optional[str] = Field(
        default=None,
        foreign_key=f"appraisal{get_table_suffix('appraisal')}._id"
    )
    type: Optional[str] = Field(default=None, sa_column=Column("type", String(64)))
    url: Optional[str] = None

    appraisal: Optional[Appraisal] = Relationship(back_populates="resources")


class AppraisalResult(SQLModel, table=True):
    """鉴定结果模型"""
    __tablename__ = f"appraisal_result{get_table_suffix('appraisal_result')}"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: str = Field(max_length=34)
    result: str = Field(nullable=False)
    notes: Optional[str] = None
    user_id: Optional[int] = Field(default=None, foreign_key=f"user{get_table_suffix('user')}.id")
    created_at: Optional[datetime] = Field(default=None, sa_column=Column("created_at"))


class UserInfo(SQLModel, table=True):
    """用户信息模型"""
    __tablename__ = f"userinfo{get_table_suffix('userinfo')}"

    id: str = Field(sa_column_kwargs={"name": "_id"}, primary_key=True)
    phone: Optional[str] = None