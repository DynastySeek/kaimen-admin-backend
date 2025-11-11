"""
鉴宝寄卖信息数据模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class AppraisalConsignment(SQLModel, table=True):
    """
    鉴宝寄卖信息模型
    """
    __tablename__ = "appraisal_consignment"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="主键信息")
    userinfo_id: Optional[str] = Field(default=None, max_length=64, description="用户信息ID")
    type: Optional[str] = Field(default=None, max_length=64, description="求购类型")
    desc: Optional[str] = Field(default=None, max_length=256, description="求购描述")
    phone: Optional[str] = Field(default=None, max_length=64, description="手机号")
    wechat_id: Optional[str] = Field(default=None, max_length=128, description="微信号")
    expected_price: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2, description="预期价格")
    is_del: Optional[str] = Field(default=None, max_length=64, description="是否删除")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="创建时间")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="更新时间")