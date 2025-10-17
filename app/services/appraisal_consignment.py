from sqlmodel import Session, select
from fastapi import Depends
from typing import Optional
from datetime import datetime

from app.models.appraisal_consignment import AppraisalConsignment
from app.schemas.appraisal_consignment import AppraisalConsignmentListData, AppraisalConsignmentItem
from app.utils.db import get_session


class AppraisalConsignmentService:
    
    @staticmethod
    def get_appraisal_consignment_list(
        page: int,
        pageSize: int,
        type: Optional[str] = None,
        phone: Optional[str] = None,
        createStartTime: Optional[str] = None,
        createEndTime: Optional[str] = None,
        session: Session = Depends(get_session)
    ) -> AppraisalConsignmentListData:
        from sqlalchemy import func, and_
        
        filters = [AppraisalConsignment.is_del == "1"]
        
        if type:
            filters.append(AppraisalConsignment.type == type)
        if phone:
            filters.append(AppraisalConsignment.phone.contains(phone))
        
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
            filters.append(AppraisalConsignment.created_at >= start_time)
        if end_time:
            filters.append(AppraisalConsignment.created_at <= end_time)
        
        query = select(AppraisalConsignment).where(and_(*filters))
        
        count_query = select(func.count(AppraisalConsignment.id)).where(and_(*filters))
        total = session.exec(count_query).one()
        
        offset = (page - 1) * pageSize
        items_query = query.offset(offset).limit(pageSize).order_by(AppraisalConsignment.created_at.desc())
        items = session.exec(items_query).all()
        
        item_list = [
            AppraisalConsignmentItem(
                id=item.id,
                type=item.type,
                desc=item.desc,
                phone=item.phone,
                expected_price=item.expected_price,
                is_del=item.is_del,
                created_at=item.created_at,
                updated_at=item.updated_at
            ) for item in items
        ]
        
        return AppraisalConsignmentListData(
            total=total,
            page=page,
            pageSize=pageSize,
            list=item_list
        )