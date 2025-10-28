"""
鉴宝寄卖关联信息数据模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class AppraisalConsignmentResource(SQLModel, table=True):
    """
    鉴宝寄卖关联信息模型
    """
    __tablename__ = "appraisal_consignment_resource"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="主键信息")
    consignment_id: int = Field(description="寄售Id")
    type: Optional[str] = Field(default=None, max_length=64, description="资源类型")
    url: Optional[str] = Field(default=None, max_length=256, description="资源url")
    is_del: Optional[str] = Field(default=None, max_length=64, description="是否删除")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="创建时间")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="更新时间")