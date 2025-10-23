from sqlmodel import Session, select
from fastapi import Depends
from typing import Optional
from datetime import datetime

from app.models.appraisal_buy import AppraisalBuy
from app.models.appraisal import UserInfo
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
        
        # 用户手机号过滤 - 通过手机号查询userinfo表获取userinfo_id
        if userPhone:
            userinfo_subquery = (
                select(UserInfo.id)
                .where(UserInfo.phone == userPhone)
            )
            userinfo_ids = session.exec(userinfo_subquery).all()
            if userinfo_ids:
                filters.append(AppraisalBuy.userinfo_id.in_(userinfo_ids))
            else:
                # 如果没有找到对应的用户，返回空结果
                filters.append(AppraisalBuy.id == -1)
        
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
        
        item_list = []
        for item in items:
            # 获取用户信息（包含手机号）
            user_info = session.exec(
                select(UserInfo).where(UserInfo.id == item.userinfo_id)
            ).first()
            
            item_list.append(AppraisalBuyItem(
                id=item.id,
                buyer_type=item.buyer_type,
                desc=item.desc,
                phone=item.phone,
                user_phone=user_info.phone if user_info else None,
                min_price=item.min_price,
                max_price=item.max_price,
                is_del=item.is_del,
                created_at=item.created_at,
                updated_at=item.updated_at
            ))
        
        return AppraisalBuyListData(
            total=total,
            page=page,
            pageSize=pageSize,
            list=item_list
        )