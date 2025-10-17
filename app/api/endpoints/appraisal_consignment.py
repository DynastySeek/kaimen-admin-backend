"""
鉴宝寄卖API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import Optional

from app.services.appraisal_consignment import AppraisalConsignmentService
from app.utils.db import get_session
from app.utils.response import success_response

router = APIRouter()


@router.get("/list")
def get_appraisal_consignment_list(
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(20, ge=1, le=100, description="每页数量"),
    type: Optional[str] = Query(None, description="寄卖类型"),
    phone: Optional[str] = Query(None, description="手机号"),
    createStartTime: Optional[str] = Query(None, description="创建开始时间"),
    createEndTime: Optional[str] = Query(None, description="创建结束时间"),
    session: Session = Depends(get_session)
):
    try:
        data = AppraisalConsignmentService.get_appraisal_consignment_list(
            page=page,
            pageSize=pageSize,
            type=type,
            phone=phone,
            createStartTime=createStartTime,
            createEndTime=createEndTime,
            session=session
        )
        
        return success_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")