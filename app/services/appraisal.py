from sqlmodel import Session, select
from fastapi import HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timezone

from app.models.appraisal import Appraisal, AppraisalResource, AppraisalResult, UserInfo
from app.models.user import User
from app.schemas.appraisal import (
    BatchDetailRequest, AppraisalDetail, LatestAppraisalData,
    BatchUpdateRequest, BatchUpdateResult, AppraisalUpdateItem,
    OrderUpdateResult, AppraisalResultBatchRequest, BatchAddResultData, FailedItem
)
from app.utils.db import get_session
from app.utils.response import success_response


class AppraisalService:

    @staticmethod
    def get_appraisal_list(
        page: int,
        pageSize: int,
        appraisalId: Optional[str] = None,
        title: Optional[str] = None,
        firstClass: Optional[str] = None,
        appraisalStatus: Optional[str] = None,
        createStartTime: Optional[str] = None,
        createEndTime: Optional[str] = None,
        updateStartTime: Optional[str] = None,
        updateEndTime: Optional[str] = None,
        appraiserId: Optional[int] = None,
        session: Session = Depends(get_session)
    ):
        from sqlalchemy import func, and_, true
        
        filters = []

        if appraisalId:
            filters.append(Appraisal.id == appraisalId)
        if title:
            filters.append(Appraisal.title.contains(title))
        if firstClass:
            filters.append(Appraisal.first_class == firstClass)
        if appraisalStatus:
            filters.append(Appraisal.appraisal_status == appraisalStatus)

        def parse_time(ts: Optional[str]) -> Optional[int]:
            try:
                return int(datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").timestamp())
            except Exception:
                return None

        # 创建时间范围过滤
        if createStartTime and (start_t := parse_time(createStartTime)):
            filters.append(Appraisal.created_at >= start_t * 1000)
        if createEndTime and (end_t := parse_time(createEndTime)):
            filters.append(Appraisal.created_at <= end_t * 1000)
            
        # 更新时间范围过滤
        if updateStartTime and (start_t := parse_time(updateStartTime)):
            filters.append(Appraisal.updatedAt >= start_t * 1000)
        if updateEndTime and (end_t := parse_time(updateEndTime)):
            filters.append(Appraisal.updatedAt <= end_t * 1000)
            
        # 鉴定师过滤 - 查询最后提交鉴定结果的鉴定师
        if appraiserId:
            # 子查询获取每个订单的最新鉴定结果
            latest_result_subquery = (
                select(AppraisalResult.order_id)
                .where(AppraisalResult.user_id == appraiserId)
                .distinct()
            )
            filters.append(Appraisal.id.in_(latest_result_subquery))

        if not filters:
            filters.append(true())
            
        total = session.exec(
            select(func.count()).select_from(Appraisal).where(and_(*filters))
        ).one()

        stmt = (
            select(Appraisal)
            .where(and_(*filters))
            .order_by(Appraisal.created_at.desc())
            .offset((page - 1) * pageSize)
            .limit(pageSize)
        )
        appraisals = session.exec(stmt).all()

        result_list = []

        for a in appraisals:
            res_stmt = select(AppraisalResource).where(AppraisalResource.appraisal_id == a.id)
            resources = session.exec(res_stmt).all()

            images, videos = [], []
            for r in resources:
                if not r.url:
                    continue
                if r.url.lower().endswith((".jpg", ".jpeg", ".png")):
                    images.append(r.url)
                elif r.url.lower().endswith((".mp4", ".mov", ".avi")):
                    videos.append(r.url)

            # 获取用户信息（包含手机号）
            user_info = session.exec(
                select(UserInfo).where(UserInfo.id == a.userinfo_id)
            ).first()

            result_list.append({
                "appraisal_id": a.id,
                "title": a.title or "",
                "user_phone": user_info.phone if user_info else None,
                "description": a.desc or "",
                "appraisal_status": a.appraisal_status or "",
                "first_class": a.first_class or "",
                "images": images,
                "videos": videos,
                "create_time": a.created_at,
            })

        return success_response(data={
            "list": result_list,
            "total": total,
            "page": page,
            "pageSize": pageSize
        })

    @staticmethod
    def get_appraisal_result(request: BatchDetailRequest, session: Session = Depends(get_session)):
        
        result_list = []
        
        for appraisal_id in request.ids:
            latest_result = session.exec(
            select(AppraisalResult).where(AppraisalResult.order_id == appraisal_id)
                .order_by(AppraisalResult.created_at.desc())
            ).first()
            print(latest_result)
            
            if not latest_result:
                continue

            # 查询鉴定师信息
            appraiser_name = ""
            appraiser_nickname = ""
            if latest_result and latest_result.user_id:
                user = session.exec(
                    select(User).where(User.id == latest_result.user_id)
                ).first()
                if user:
                    appraiser_name = user.name or ""
                    appraiser_nickname = user.nickname or ""
            
            latest_appraisal_data = {
                "appraisal_id": appraisal_id,
                "created_at": str(latest_result.created_at or 0),
                "result": latest_result.result,
                "comment": latest_result.notes if latest_result else "",
                "appraiser_name": appraiser_name,
                "appraiser_nickname": appraiser_nickname
            }
            
            result_list.append(latest_appraisal_data)
            
        return success_response(data=result_list, message="查询成功")

    @staticmethod
    def batch_update_appraisals(request: BatchUpdateRequest, session: Session = Depends(get_session)):
        
        success_count = 0
        failed_items = []
        
        for item in request.items:
            try:
                appraisal = session.exec(
                    select(Appraisal).where(Appraisal.id == item.order_id)
                ).first()
                
                if not appraisal:
                    failed_items.append(FailedItem(
                        order_id=item.order_id,
                        reason="订单不存在"
                    ))
                    continue
                
                if item.appraisal_status is not None:
                    appraisal.appraisal_status = str(item.appraisal_status)
                if item.appraisal_result is not None:
                    appraisal.appraisal_result = str(item.appraisal_result)
                if item.notes:
                    appraisal.notes = item.notes
                
                # 更新时间
                appraisal.updatedAt = int(datetime.now(timezone.utc).timestamp() * 1000)
                
                session.add(appraisal)
                success_count += 1
                
            except Exception as e:
                failed_items.append(FailedItem(
                    order_id=item.order_id,
                    reason=str(e)
                ))
        
        session.commit()
        
        return success_response(data={
            "success_count": success_count,
            "failed_count": len(failed_items),
            "failed_items": [item.dict() for item in failed_items]
        })

    @staticmethod
    def batch_update_orders(items: List[AppraisalUpdateItem], session: Session = Depends(get_session)):
        
        results = []
        
        for item in items:
            try:
                appraisal = session.exec(
                    select(Appraisal).where(Appraisal.id == item.order_id)
                ).first()
                
                if not appraisal:
                    results.append({
                        "order_id": item.order_id,
                        "success": False,
                        "message": "订单不存在"
                    })
                    continue
                
                if item.appraisal_status is not None:
                    appraisal.appraisal_status = str(item.appraisal_status)
                if item.appraisal_result is not None:
                    appraisal.appraisal_result = str(item.appraisal_result)
                if item.notes:
                    appraisal.notes = item.notes
                
                # 更新时间
                appraisal.updatedAt = int(datetime.now(timezone.utc).timestamp() * 1000)
                
                session.add(appraisal)
                
                results.append({
                    "order_id": item.order_id,
                    "success": True,
                    "message": "更新成功"
                })
                
            except Exception as e:
                results.append({
                    "order_id": item.order_id,
                    "success": False,
                    "message": str(e)
                })
        
        session.commit()
        
        return success_response(data=results)

    @staticmethod
    def batch_add_appraisal_results(request: AppraisalResultBatchRequest, session: Session = Depends(get_session)):
        
        success_count = 0
        failed_items = []
        
        for item in request.items:
            try:
                appraisal = session.exec(
                    select(Appraisal).where(Appraisal.id == item.order_id)
                ).first()
                
                if not appraisal:
                    failed_items.append({
                        "order_id": item.order_id,
                        "reason": "订单不存在"
                    })
                    continue
                
                result = AppraisalResult(
                    appraisal_id=item.order_id,
                    user_id=item.user_id,
                    result=str(item.result),
                    notes=item.notes or "",
                    created_at=datetime.now(timezone.utc)
                )
                
                session.add(result)
                success_count += 1
                
            except Exception as e:
                failed_items.append({
                    "order_id": item.order_id,
                    "reason": str(e)
                })
        
        session.commit()
        
        return success_response(data={
            "success_count": success_count,
            "failed_count": len(failed_items),
            "failed_items": failed_items
        })