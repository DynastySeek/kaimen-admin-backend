"""
用户信息数据模型
"""
from sqlmodel import SQLModel, Field, Column, String
from typing import Optional
from datetime import datetime
from decimal import Decimal

class GoldExchange(SQLModel, table=True):
    """用户信息模型"""
    __tablename__ = "gold_exchange"
    id: Optional[int] = Field(default=None, primary_key=True)
    type: Optional[int] = Field(sa_column=Column("type", default=1))
    userinfo_id: Optional[str]= Field(sa_column=Column("userinfo_id", String(34))) 
    remain_tips: Optional[Decimal] = Decimal('0.0')
    gold_gram: Optional[Decimal] = Decimal('0.0')
    gold_price: Optional[Decimal] = Decimal('0.0')
   