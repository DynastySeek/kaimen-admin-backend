from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class AppraisalBuyItem(BaseModel):
    id: int
    buyer_type: Optional[str] = None
    desc: Optional[str] = None
    phone: Optional[str] = None
    user_phone: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    is_del: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AppraisalBuyListData(BaseModel):
    total: int
    page: int
    pageSize: int
    list: List[AppraisalBuyItem]