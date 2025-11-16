"""
鉴定订单数据模型
"""
from sqlmodel import SQLModel, Field, Relationship, Column, String
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .appraisal_resource import AppraisalResource


class Appraisal(SQLModel, table=True):
    """鉴定订单模型"""
    __tablename__ = "appraisal"

    id: str = Field(sa_column=Column("_id", String(34), primary_key=True))
    title: Optional[str] = None
    desc: Optional[str] = Field(default=None, sa_column=Column("desc", String(255)))
    appraisal_status: Optional[str] = None
    first_class: Optional[str] = None
    created_at: Optional[int] = Field(default=None, sa_column=Column("createdAt"))
    updated_at: Optional[int] = Field(default=None, sa_column=Column("updatedAt"))
    userinfo_id: Optional[str] = Field(default=None, sa_column=Column("userinfo_id", String(64)))
    #wxchatId: Optional[str]= Field(default=None,sa_column=Column("wechat_id",String(128)), description="微信")
    last_appraiser_id: Optional[int] = Field(default=None, description="最新鉴定人id")
    last_appraisal_result_id: Optional[int] = Field(default=None, description="最新鉴定结果id")
    appraisal_result: Optional[str] = Field(default=None, max_length=64, description="鉴定结果")
    fine_class: Optional[int] = 0
    appraisal_business_type: Optional[str] = None    
    phone: Optional[str] = None
    wechat_id: Optional[str] = None
    fine_tips: Optional[int] = 0
    resources: List["AppraisalResource"] = Relationship(back_populates="appraisal")