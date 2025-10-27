from sqlmodel import Session, select
from fastapi import Depends
from typing import Optional
from datetime import datetime

from app.models.appraisal_consignment import AppraisalConsignment
from app.models.appraisal_consignment_resource import AppraisalConsignmentResource
from app.models.user_info import UserInfo
from app.schemas.appraisal_consignment import AppraisalConsignmentListData, AppraisalConsignmentItem
from app.utils.db import get_session


class AppraisalConsignmentService:
    
    @staticmethod
    def get_appraisal_consignment_list(
        page: int,
        pageSize: int,
        id: Optional[str] = None,
        type: Optional[str] = None,
        desc: Optional[str] = None,
        minExpectedPrice: Optional[float] = None,
        maxExpectedPrice: Optional[float] = None,
        userPhone: Optional[str] = None,
        phone: Optional[str] = None,
        createStartTime: Optional[str] = None,
        createEndTime: Optional[str] = None,
        session: Session = Depends(get_session)
    ) -> AppraisalConsignmentListData:
        from sqlalchemy import func, and_
        
        filters = [AppraisalConsignment.is_del == "1"]
        
        if id:
            filters.append(AppraisalConsignment.id == int(id))
        if type:
            filters.append(AppraisalConsignment.type.contains(type))
        if desc:
            filters.append(AppraisalConsignment.desc.contains(desc))
        if minExpectedPrice is not None:
            filters.append(AppraisalConsignment.expected_price >= minExpectedPrice)
        if maxExpectedPrice is not None:
            filters.append(AppraisalConsignment.expected_price <= maxExpectedPrice)
        # 用户手机号过滤 - 通过手机号查询userinfo表获取userinfo_id
        if userPhone:
            userinfo_subquery = (
                select(UserInfo.id)
                .where(UserInfo.phone == userPhone)
            )
            userinfo_ids = session.exec(userinfo_subquery).all()
            if userinfo_ids:
                filters.append(AppraisalConsignment.userinfo_id.in_(userinfo_ids))
            else:
                # 如果没有找到对应的用户，返回空结果
                filters.append(AppraisalConsignment.id == -1)
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
        
        if not items:
            return AppraisalConsignmentListData(
                total=total,
                page=page,
                pageSize=pageSize,
                list=[]
            )
        
        # 批量获取所有需要的数据，避免 N+1 查询问题
        item_ids = [item.id for item in items]
        userinfo_ids = [item.userinfo_id for item in items if item.userinfo_id]
        
        # 批量查询资源信息
        resources_stmt = select(AppraisalConsignmentResource).where(
            AppraisalConsignmentResource.consignment_id.in_(item_ids)
        )
        all_resources = session.exec(resources_stmt).all()
        
        # 按 consignment_id 分组资源
        resources_by_id = {}
        for resource in all_resources:
            if resource.consignment_id not in resources_by_id:
                resources_by_id[resource.consignment_id] = []
            resources_by_id[resource.consignment_id].append(resource)
        
        # 批量查询用户信息
        user_info_map = {}
        if userinfo_ids:
            user_infos_stmt = select(UserInfo).where(UserInfo.id.in_(userinfo_ids))
            user_infos = session.exec(user_infos_stmt).all()
            user_info_map = {user.id: user for user in user_infos}
        
        # 构建结果列表
        item_list = []
        for item in items:
            # 处理资源信息
            resources = resources_by_id.get(item.id, [])
            images, videos = [], []
            for r in resources:
                if not r.url:
                    continue
                if r.url.lower().endswith((".jpg", ".jpeg", ".png")):
                    images.append(r.url)
                elif r.url.lower().endswith((".mp4", ".mov", ".avi")):
                    videos.append(r.url)

            # 获取用户信息
            user_info = user_info_map.get(item.userinfo_id)

            item_list.append(AppraisalConsignmentItem(
                id=item.id,
                type=item.type,
                desc=item.desc,
                phone=item.phone,
                user_phone=user_info.phone if user_info else None,
                expected_price=item.expected_price,
                is_del=item.is_del,
                images=images,
                videos=videos,
                created_at=item.created_at,
                updated_at=item.updated_at
            ))
        
        return AppraisalConsignmentListData(
            total=total,
            page=page,
            pageSize=pageSize,
            list=item_list
        )