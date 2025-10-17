"""
鉴宝求购相关数据模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.config.settings import get_table_suffix


class AppraisalBuy(SQLModel, table=True):
    """
    鉴宝求购信息模型
    """
    __tablename__ = f"appraisal_buy{get_table_suffix('appraisal_buy')}"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="主键信息")
    buyer_type: Optional[str] = Field(default=None, max_length=64, description="求购类型")
    desc: Optional[str] = Field(default=None, max_length=256, description="求购描述")
    phone: Optional[str] = Field(default=None, max_length=64, description="手机号")
    min_price: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2, description="最低期望价格")
    max_price: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2, description="最高期望价格")
    is_del: Optional[str] = Field(default=None, max_length=64, description="是否删除")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="创建时间")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="更新时间")