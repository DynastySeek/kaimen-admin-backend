"""
鉴宝寄卖信息相关数据模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.config.settings import get_table_suffix


class AppraisalConsignment(SQLModel, table=True):
    """
    鉴宝寄卖信息模型
    """
    __tablename__ = f"appraisal_consignment{get_table_suffix('appraisal_consignment')}"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="主键信息")
    type: Optional[str] = Field(default=None, max_length=64, description="求购类型")
    desc: Optional[str] = Field(default=None, max_length=256, description="求购描述")
    phone: Optional[str] = Field(default=None, max_length=64, description="手机号")
    expected_price: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2, description="预期价格")
    is_del: Optional[str] = Field(default=None, max_length=64, description="是否删除")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="创建时间")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="更新时间")


class AppraisalConsignmentResourcePreview(SQLModel, table=True):
    """
    鉴宝寄卖关联信息模型
    """
    __tablename__ = "appraisal_consignment_resource_preview"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="主键信息")
    consignment_id: int = Field(description="寄售Id")
    type: Optional[str] = Field(default=None, max_length=64, description="资源类型")
    url: Optional[str] = Field(default=None, max_length=256, description="资源url")
    is_del: Optional[str] = Field(default=None, max_length=64, description="是否删除")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="创建时间")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="更新时间")