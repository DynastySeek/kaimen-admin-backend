from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class AppraisalConsignmentItem(BaseModel):
    id: int
    type: Optional[str] = None
    desc: Optional[str] = None
    phone: Optional[str] = None
    expected_price: Optional[Decimal] = None
    is_del: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AppraisalConsignmentListData(BaseModel):
    total: int
    page: int
    pageSize: int
    list: List[AppraisalConsignmentItem]