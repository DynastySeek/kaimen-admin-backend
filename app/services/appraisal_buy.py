from sqlmodel import Session, select
from fastapi import Depends
from typing import Optional
from datetime import datetime

from app.models.appraisal_buy import AppraisalBuy
from app.schemas.appraisal_buy import AppraisalBuyListData, AppraisalBuyItem
from app.utils.db import get_session


class AppraisalBuyService:
    
    @staticmethod
    def get_appraisal_buy_list(
        page: int,
        pageSize: int,
        id: Optional[str] = None,
        buyer_type: Optional[str] = None,
        desc: Optional[str] = None,
        minPrice: Optional[float] = None,
        maxPrice: Optional[float] = None,
        userPhone: Optional[str] = None,
        phone: Optional[str] = None,
        createStartTime: Optional[str] = None,
        createEndTime: Optional[str] = None,
        session: Session = Depends(get_session)
    ) -> AppraisalBuyListData:
        from sqlalchemy import func, and_
        
        filters = [AppraisalBuy.is_del == "1"]
        
        if id:
            filters.append(AppraisalBuy.id == id)
        
        if buyer_type:
            filters.append(AppraisalBuy.buyer_type == buyer_type)
        
        if desc:
            filters.append(AppraisalBuy.desc.like(f"%{desc}%"))
        
        if minPrice is not None:
            filters.append(AppraisalBuy.min_price >= minPrice)
        
        if maxPrice is not None:
            filters.append(AppraisalBuy.max_price <= maxPrice)
        
        if userPhone:
            filters.append(AppraisalBuy.phone == userPhone)
        
        if phone:
            filters.append(AppraisalBuy.phone.like(f"%{phone}%"))
        
        def parse_time(ts: Optional[str]) -> Optional[datetime]:
            if not ts:
                return None
            try:
                return datetime.fromisoformat(ts.replace('Z', '+00:00'))
            except ValueError:
                return None
        
        start_time = parse_time(createStartTime)
        end_time = parse_time(createEndTime)
        
        if start_time:
            filters.append(AppraisalBuy.created_at >= start_time)
        if end_time:
            filters.append(AppraisalBuy.created_at <= end_time)
        
        query = select(AppraisalBuy).where(and_(*filters))
        
        count_query = select(func.count(AppraisalBuy.id)).where(and_(*filters))
        total = session.exec(count_query).one()
        
        offset = (page - 1) * pageSize
        items_query = query.offset(offset).limit(pageSize).order_by(AppraisalBuy.created_at.desc())
        items = session.exec(items_query).all()
        
        item_list = [
            AppraisalBuyItem(
                id=item.id,
                buyer_type=item.buyer_type,
                desc=item.desc,
                phone=item.phone,
                min_price=item.min_price,
                max_price=item.max_price,
                is_del=item.is_del,
                created_at=item.created_at,
                updated_at=item.updated_at
            ) for item in items
        ]
        
        return AppraisalBuyListData(
            total=total,
            page=page,
            pageSize=pageSize,
            list=item_list
        )