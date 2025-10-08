from sqlmodel import Session, select
from fastapi import HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timezone

from app.models.appraisal import Appraisal, AppraisalResource, AppraisalResult, UserInfo
from app.schemas.appraisal import (
    BatchDetailRequest, AppraisalDetail, LatestAppraisalData,
    BatchUpdateRequest, BatchUpdateResult, AppraisalUpdateItem,
    OrderUpdateResult, AppraisalResultBatchRequest, BatchAddResultData, FailedItem
)
from app.utils.db import get_session


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
            filters.append(Appraisal.appraisal_create_time >= start_t * 1000)
        if createEndTime and (end_t := parse_time(createEndTime)):
            filters.append(Appraisal.appraisal_create_time <= end_t * 1000)
            
        # 更新时间范围过滤
        if updateStartTime and (start_t := parse_time(updateStartTime)):
            filters.append(Appraisal.appraisal_update_time >= start_t * 1000)
        if updateEndTime and (end_t := parse_time(updateEndTime)):
            filters.append(Appraisal.appraisal_update_time <= end_t * 1000)
            
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
            .order_by(Appraisal.appraisal_create_time.desc())
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

            result_list.append({
                "appraisal_id": a.id,
                "title": a.title or "",
                "description": a.desc or "",
                "appraisal_status": a.appraisal_status or "",
                "first_class": a.first_class or "",
                "images": images,
                "videos": videos,
                "create_time": a.appraisal_create_time,
            })

        return {
            "code": 200,
            "message": "查询成功",
            "data": {
                "total": total,
                "page": page,
                "page_size": pageSize,
                "total_pages": (total + pageSize - 1) // pageSize,
                "list": result_list,
            },
        }

    @staticmethod
    def get_batch_details(request: BatchDetailRequest, session: Session = Depends(get_session)) -> List[AppraisalDetail]:
        details = []
        
        for order_id in request.ids:
            appraisal = session.exec(
                select(Appraisal).where(Appraisal.id == order_id)
            ).first()
            
            if not appraisal:
                continue
                
            user_info = session.exec(
                select(UserInfo).where(UserInfo.id == appraisal.userinfo_id)
            ).first()
            
            latest_result = session.exec(
                select(AppraisalResult).where(AppraisalResult.order_id == order_id)
                .order_by(AppraisalResult.created_at.desc())
            ).first()
            
            latest_appraisal = LatestAppraisalData(
                id=order_id,
                user_id=appraisal.userinfo_id or "",
                create_time=str(appraisal.appraisal_create_time or 0),
                update_time="",
                appraisal_status=int(appraisal.appraisal_status or 0),
                appraisal_result=latest_result.result if latest_result else "",
                notes=latest_result.notes if latest_result else "",
                result=latest_result.result if latest_result else "",
                reasons=[],
                custom_reason=""
            )
            
            detail = AppraisalDetail(
                order_id=order_id,
                title=appraisal.title or "",
                user_phone=user_info.phone if user_info else None,
                description=appraisal.desc or "",
                appraisal_class=appraisal.first_class or "",
                create_time=str(appraisal.appraisal_create_time or 0),
                latest_appraisal=latest_appraisal
            )
            
            details.append(detail)
            
        return details

    @staticmethod
    def batch_update_appraisals(request: BatchUpdateRequest, session: Session = Depends(get_session)) -> BatchUpdateResult:
        success_count = 0
        failed_count = 0
        failed_items = []
        
        for item in request.items:
            try:
                appraisal = session.exec(
                    select(Appraisal).where(Appraisal.id == item.appraisalId)
                ).first()
                
                if not appraisal:
                    failed_count += 1
                    failed_items.append(item.appraisalId)
                    continue
                
                if item.appraisalClass is not None:
                    appraisal.first_class = item.appraisalClass
                
                if item.appraisalResult is not None:
                    appraisal.appraisal_status = str(item.appraisalResult)
                
                session.add(appraisal)
                
                if item.comment or item.appraisalResult is not None:
                    result = AppraisalResult(
                        order_id=item.appraisalId,
                        result=str(item.appraisalResult) if item.appraisalResult is not None else "",
                        notes=item.comment or "",
                        created_at=datetime.now(timezone.utc)
                    )
                    session.add(result)
                
                success_count += 1
                
            except Exception as e:
                failed_count += 1
                failed_items.append(item.appraisalId)
        
        session.commit()
        
        return BatchUpdateResult(
            success_count=success_count,
            failed_count=failed_count,
            failed_items=failed_items
        )

    @staticmethod
    def batch_update_orders(items: List[AppraisalUpdateItem], session: Session = Depends(get_session)) -> List[OrderUpdateResult]:
        results = []
        
        for item in items:
            try:
                appraisal = session.exec(
                    select(Appraisal).where(Appraisal.id == item.id)
                ).first()
                
                if not appraisal:
                    results.append(OrderUpdateResult(
                        order_id=item.id,
                        success=False,
                        message="订单不存在"
                    ))
                    continue
                
                if item.appraisal_status is not None:
                    appraisal.appraisal_status = str(item.appraisal_status)
                
                if item.appraisal_class is not None:
                    appraisal.first_class = item.appraisal_class
                
                session.add(appraisal)
                
                results.append(OrderUpdateResult(
                    order_id=item.id,
                    success=True,
                    message="更新成功"
                ))
                
            except Exception as e:
                results.append(OrderUpdateResult(
                    order_id=item.id,
                    success=False,
                    message=f"更新失败: {str(e)}"
                ))
        
        session.commit()
        return results

    @staticmethod
    def batch_add_appraisal_results(request: AppraisalResultBatchRequest, session: Session = Depends(get_session)) -> BatchAddResultData:
        success_count = 0
        failed_count = 0
        failed_items = []
        
        for item in request.items:
            try:
                appraisal = session.exec(
                    select(Appraisal).where(Appraisal.id == item.orderid)
                ).first()
                
                if not appraisal:
                    failed_count += 1
                    failed_items.append(FailedItem(
                        order_id=int(item.orderid) if item.orderid.isdigit() else 0,
                        reason="订单不存在"
                    ))
                    continue
                
                result = AppraisalResult(
                    order_id=item.orderid,
                    result=item.appraisalResult or "",
                    notes=item.comment or "",
                    user_id=item.userid,
                    created_at=datetime.now(timezone.utc)
                )
                
                session.add(result)
                success_count += 1
                
            except Exception as e:
                failed_count += 1
                failed_items.append(FailedItem(
                    order_id=int(item.orderid) if item.orderid.isdigit() else 0,
                    reason=f"添加失败: {str(e)}"
                ))
        
        session.commit()
        
        return BatchAddResultData(
            success_count=success_count,
            failed_count=failed_count,
            failed_items=failed_items
        )