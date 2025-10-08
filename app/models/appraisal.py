"""
鉴定相关的数据模型
"""
from sqlmodel import SQLModel, Field, Relationship, Column, String
from typing import Optional, List
from datetime import datetime, timezone


class Appraisal(SQLModel, table=True):
    """鉴定订单模型"""
    __tablename__ = "appraisal"

    id: str = Field(sa_column=Column("_id", String(34), primary_key=True))
    title: Optional[str] = None
    desc: Optional[str] = Field(default=None, sa_column=Column("desc", String(255)))
    appraisal_status: Optional[str] = None
    first_class: Optional[str] = None
    appraisal_create_time: Optional[int] = None
    userinfo_id: Optional[str] = Field(default=None, sa_column=Column("userinfo_id", String(64)))

    resources: List["AppraisalResource"] = Relationship(back_populates="appraisal")


class AppraisalResource(SQLModel, table=True):
    """鉴定资源模型"""
    __tablename__ = "appraisal_resource"

    id: str = Field(sa_column=Column("_id", String(34), primary_key=True))
    appraisal_id: Optional[str] = Field(
        default=None,
        foreign_key="appraisal._id"
    )
    type: Optional[str] = Field(default=None, sa_column=Column("type", String(64)))
    url: Optional[str] = None

    appraisal: Optional[Appraisal] = Relationship(back_populates="resources")


class AppraisalResult(SQLModel, table=True):
    """鉴定结果模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: str = Field(max_length=34)
    result: str = Field(nullable=False)
    notes: Optional[str] = None
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserInfo(SQLModel, table=True):
    """用户信息模型"""
    __tablename__ = "userinfo"

    id: str = Field(sa_column_kwargs={"name": "_id"}, primary_key=True)
    phone: Optional[str] = None