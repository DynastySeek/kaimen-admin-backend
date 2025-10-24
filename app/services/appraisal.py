from sqlmodel import Session, select
from fastapi import HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timezone
import logging

from app.models.appraisal import Appraisal, AppraisalResource, AppraisalResult, UserInfo
from app.models.user import User
from app.schemas.appraisal import (
    BatchDetailRequest, AppraisalDetail, LatestAppraisalData,
    BatchUpdateRequest, BatchUpdateResult, AppraisalUpdateItem,
    OrderUpdateResult, AppraisalResultBatchRequest, BatchAddResultData, FailedItem
)
from app.utils.db import get_session
from app.utils.response import success_response
from app.core.dependencies import get_current_user_required
from app.services.sms import get_sms_service, get_sms_delay_manager
from app.services.appraisal_stats import get_appraisal_stats_service

logger = logging.getLogger(__name__)



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
        lastAppraiserId: Optional[int] = None,
        userPhone: Optional[str] = None,
        appraisalResult: Optional[str] = None,
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
            filters.append(Appraisal.updated_at >= start_t * 1000)
        if updateEndTime and (end_t := parse_time(updateEndTime)):
            filters.append(Appraisal.updated_at <= end_t * 1000)
        # 鉴定师过滤 - 查询最后提交鉴定结果的鉴定师
        if lastAppraiserId:
            filters.append(Appraisal.last_appraiser_id == lastAppraiserId)
        # 鉴定结果过滤
        if appraisalResult:
            filters.append(Appraisal.appraisal_result == appraisalResult)

        # 用户手机号过滤 - 通过手机号查询userinfo表获取userinfo_id
        if userPhone:
            userinfo_subquery = (
                select(UserInfo.id)
                .where(UserInfo.phone == userPhone)
            )
            userinfo_ids = session.exec(userinfo_subquery).all()
            if userinfo_ids:
                filters.append(Appraisal.userinfo_id.in_(userinfo_ids))
            else:
                # 如果没有找到对应的用户，返回空结果
                filters.append(Appraisal.id == -1)

        if not filters:
            filters.append(true())
            
        total = session.exec(
            select(func.count()).select_from(Appraisal).where(and_(*filters))
        ).one()

        stmt = (
            select(Appraisal)
            .where(and_(*filters))
            .order_by(Appraisal.updated_at.asc())
            .offset((page - 1) * pageSize)
            .limit(pageSize)
        )
        appraisals = session.exec(stmt).all()

        # 批量查询优化：收集所有需要的ID
        appraisal_ids = [a.id for a in appraisals]
        userinfo_ids = [a.userinfo_id for a in appraisals if a.userinfo_id]

        # 批量查询所有资源
        resources_map = {}
        if appraisal_ids:
            resources_stmt = select(AppraisalResource).where(AppraisalResource.appraisal_id.in_(appraisal_ids))
            all_resources = session.exec(resources_stmt).all()
            
            for resource in all_resources:
                if resource.appraisal_id not in resources_map:
                    resources_map[resource.appraisal_id] = []
                resources_map[resource.appraisal_id].append(resource)

        # 批量查询所有用户信息
        userinfo_map = {}
        if userinfo_ids:
            userinfo_stmt = select(UserInfo).where(UserInfo.id.in_(userinfo_ids))
            all_userinfo = session.exec(userinfo_stmt).all()
            
            for userinfo in all_userinfo:
                userinfo_map[userinfo.id] = userinfo

        # 批量查询所有鉴定结果
        appraisal_result_ids = [a.last_appraisal_result_id for a in appraisals if a.last_appraisal_result_id]
        appraisal_result_map = {}
        if appraisal_result_ids:
            appraisal_result_stmt = select(AppraisalResult).where(AppraisalResult.id.in_(appraisal_result_ids))
            all_appraisal_results = session.exec(appraisal_result_stmt).all()
            
            for appraisal_result in all_appraisal_results:
                appraisal_result_map[appraisal_result.id] = appraisal_result

        # 批量查询所有鉴定师用户信息
        appraiser_ids = [a.last_appraiser_id for a in appraisals if a.last_appraiser_id]
        appraiser_map = {}
        if appraiser_ids:
            appraiser_stmt = select(User).where(User.id.in_(appraiser_ids))
            all_appraisers = session.exec(appraiser_stmt).all()
            
            for appraiser in all_appraisers:
                appraiser_map[appraiser.id] = appraiser

        result_list = []

        for a in appraisals:
            # 从缓存中获取资源
            resources = resources_map.get(a.id, [])
            
            images, videos = [], []
            for r in resources:
                if not r.url:
                    continue
                if r.url.lower().endswith((".jpg", ".jpeg", ".png")):
                    images.append(r.url)
                elif r.url.lower().endswith((".mp4", ".mov", ".avi")):
                    videos.append(r.url)

            # 从缓存中获取用户信息
            user_info = userinfo_map.get(a.userinfo_id)

            # 从缓存中获取鉴定结果信息
            last_appraisal_result = appraisal_result_map.get(a.last_appraisal_result_id)
            last_appraisal_result_data = None
            if last_appraisal_result:
                last_appraisal_result_data = {
                    "id": last_appraisal_result.id,
                    "appraisal_id": last_appraisal_result.appraisal_id,
                    "result": last_appraisal_result.result,
                    "notes": last_appraisal_result.notes,
                    "user_id": last_appraisal_result.user_id,
                }

            # 从缓存中获取鉴定师信息
            last_appraiser = appraiser_map.get(a.last_appraiser_id)
            last_appraiser_data = None
            if last_appraiser:
                last_appraiser_data = {
                    "id": last_appraiser.id,
                    "name": last_appraiser.name,
                    "nickname": last_appraiser.nickname,
                }

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
                "appraisal_result": a.appraisal_result,
                "last_appraiser_id": a.last_appraiser_id,
                "last_appraisal_result_id": a.last_appraisal_result_id,
                "last_appraisal_result": last_appraisal_result_data,
                "last_appraiser": last_appraiser_data,
            })

        return success_response(data={
            "list": result_list,
            "total": total,
            "page": page,
            "pageSize": pageSize
        })

    @staticmethod
    def batch_update_appraisals(request: List[AppraisalUpdateItem], session: Session = Depends(get_session)):
        
        success_count = 0
        failed_items = []
        stats_service = get_appraisal_stats_service()
        sms_service = get_sms_service()
        
        for item in request:
            try:
                appraisal = session.exec(
                    select(Appraisal).where(Appraisal.id == item.id)
                ).first()
                
                if not appraisal:
                    failed_items.append(FailedItem(
                        appraisal_id=item.id,
                        reason="鉴定不存在"
                    ))
                    continue
                
                # 记录旧状态用于统计更新
                old_status = appraisal.appraisal_status
                
                if item.appraisal_status is not None:
                    appraisal.appraisal_status = str(item.appraisal_status)
                if item.appraisal_class is not None:
                    appraisal.first_class = str(item.appraisal_class)
                
                session.add(appraisal)
                success_count += 1
                
                # 更新统计数据
                if appraisal.userinfo_id:
                    stats_service.handle_status_change(
                        userinfo_id=appraisal.userinfo_id,
                        appraisal_id=appraisal.id,
                        old_status=old_status,
                        new_status=appraisal.appraisal_status
                    )

                # 检测状态变更，如果变更为需要通知的状态则发送短信
                if old_status != appraisal.appraisal_status and appraisal.appraisal_status in ["3", "4", "5"]:
                    logger.info(
                        f"检测到状态变更为需要通知的状态: 订单ID={item.id}, "
                        f"旧状态={old_status}, 新状态={appraisal.appraisal_status}"
                    )
                    
                    # 查询用户手机号
                    user_info = session.exec(
                        select(UserInfo).where(UserInfo.id == appraisal.userinfo_id)
                    ).first()
                    
                    if user_info and user_info.phone:
                        # 使用延迟发送管理器
                        delay_manager = get_sms_delay_manager()
                        if delay_manager:
                            try:
                                delay_manager.schedule_delayed_sms(
                                    appraisal_id=str(item.id),
                                    phone=user_info.phone,
                                    status=appraisal.appraisal_status
                                )
                                logger.info(
                                    f"已调度延迟状态通知短信: 订单ID={item.id}, "
                                    f"状态={appraisal.appraisal_status}, 手机号={user_info.phone}"
                                )
                            except Exception as delay_error:
                                # 延迟发送失败不影响主业务流程
                                logger.error(
                                    f"延迟状态通知短信调度失败: 订单ID={item.id}, "
                                    f"错误={str(delay_error)}",
                                    exc_info=True
                                )
                        else:
                            logger.warning("延迟发送管理器未初始化，跳过状态通知短信发送")
                    else:
                        logger.warning(
                            f"未找到用户手机号，跳过状态通知短信发送: "
                            f"订单ID={item.id}, userinfo_id={appraisal.userinfo_id}"
                        )
                
            except Exception as e:
                failed_items.append(FailedItem(
                    appraisal_id=item.id,
                    reason=str(e)
                ))
        
        session.commit()
        
        return success_response(data={
            "success_count": success_count,
            "failed_count": len(failed_items),
            "failed_items": [item.dict() for item in failed_items]
        })

    @staticmethod
    def batch_add_appraisal_results(
        request: AppraisalResultBatchRequest, 
        current_user: User = Depends(get_current_user_required),
        session: Session = Depends(get_session)
    ):
        
        success_count = 0
        failed_items = []
        
        # 获取短信服务实例
        sms_service = get_sms_service()
        
        # 获取统计服务实例
        stats_service = get_appraisal_stats_service()
        
        for item in request.items:
            try:
                appraisal = session.exec(
                    select(Appraisal).where(Appraisal.id == item.appraisalId)
                ).first()
                
                if not appraisal:
                    failed_items.append(FailedItem(
                        appraisal_id=item.appraisalId,
                        reason="订单不存在"
                    ))
                    continue
                
                # 记录旧状态用于统计更新
                old_status = appraisal.appraisal_status
                
                # 生成备注内容
                notes = item.comment or ""
                if item.reasons:
                    notes += f" | 原因: {', '.join(item.reasons)}"
                
                result = AppraisalResult(
                    appraisal_id=item.appraisalId,
                    user_id=current_user.id,
                    result=item.appraisalResult,
                    notes=notes,
                    created_at=datetime.now(timezone.utc)
                )
                
                session.add(result)
                session.flush()  # 获取新插入记录的ID
                
                # 更新Appraisal的字段
                appraisal.last_appraiser_id = current_user.id
                appraisal.last_appraisal_result_id = result.id
                appraisal.appraisal_result = item.appraisalResult
                appraisal.appraisal_status = "3"  # 添加鉴定结果后自动设置为已完成状态
                
                session.add(appraisal)
                success_count += 1
                
                # 只有当鉴定结果为真(1)或假(2)时，才更新统计数据
                if item.appraisalResult in ["1", "2"] and appraisal.userinfo_id:
                    stats_service.handle_status_change(
                        userinfo_id=appraisal.userinfo_id,
                        appraisal_id=appraisal.id,
                        old_status=old_status,
                        new_status=appraisal.appraisal_status
                    )
                
                # 检测状态是否变更为已完结，如果是则发送短信通知
                if old_status != appraisal.appraisal_status and appraisal.appraisal_status == "3":
                    logger.info(
                        f"检测到状态变更为已完结: 订单ID={item.appraisalId}, "
                        f"旧状态={old_status}, 新状态={appraisal.appraisal_status}"
                    )
                    
                    # 查询用户手机号
                    user_info = session.exec(
                        select(UserInfo).where(UserInfo.id == appraisal.userinfo_id)
                    ).first()
                    
                    if user_info and user_info.phone:
                        # 使用延迟发送管理器
                        delay_manager = get_sms_delay_manager()
                        if delay_manager:
                            try:
                                delay_manager.schedule_delayed_sms(
                                    appraisal_id=str(item.appraisalId),
                                    phone=user_info.phone,
                                    status=appraisal.appraisal_status
                                )
                                logger.info(
                                    f"已调度延迟状态通知短信: 订单ID={item.appraisalId}, "
                                    f"状态={appraisal.appraisal_status}, 手机号={user_info.phone}"
                                )
                            except Exception as delay_error:
                                # 延迟发送失败不影响主业务流程
                                logger.error(
                                    f"延迟状态通知短信调度失败: 订单ID={item.appraisalId}, "
                                    f"错误={str(delay_error)}",
                                    exc_info=True
                                )
                        else:
                            logger.warning("延迟发送管理器未初始化，跳过状态通知短信发送")
                    else:
                        logger.warning(
                            f"未找到用户手机号，跳过状态通知短信发送: "
                            f"订单ID={item.appraisalId}, userinfo_id={appraisal.userinfo_id}"
                        )
                
            except Exception as e:
                failed_items.append(FailedItem(
                    appraisal_id=item.appraisalId,
                    reason=str(e)
                ))
        
        session.commit()
        
        return success_response(data=BatchAddResultData(
            success_count=success_count,
            failed_count=len(failed_items),
            failed_items=failed_items
        ))