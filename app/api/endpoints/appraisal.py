from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional

from app.schemas.appraisal import (
    BatchDetailRequest, BatchDetailResponse, AppraisalDetail,
    BatchUpdateRequest, BatchUpdateResponse,
    AppraisalUpdateItem, OrderUpdateResponse,
    AppraisalResultBatchRequest, BatchAddResultResponse
)
from app.services.appraisal import AppraisalService
from app.utils.db import get_session
from app.utils.response import success_response

router = APIRouter()


@router.get("/list")
def get_appraisal_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1),
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
    try:
        result = AppraisalService.get_appraisal_list(
            page=page,
            pageSize=pageSize,
            appraisalId=appraisalId,
            title=title,
            firstClass=firstClass,
            appraisalStatus=appraisalStatus,
            createStartTime=createStartTime,
            createEndTime=createEndTime,
            updateStartTime=updateStartTime,
            updateEndTime=updateEndTime,
            appraiserId=appraiserId,
            session=session
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取鉴定列表失败: {str(e)}")


@router.post("/result")
def get_appraisal_result(
    request: BatchDetailRequest,
    session: Session = Depends(get_session)
):
    try:
        result = AppraisalService.get_appraisal_result(request, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取鉴定详情失败: {str(e)}")


@router.post("/update")
def batch_update_appraisals(
    items: List[AppraisalUpdateItem],
    session: Session = Depends(get_session)
):
    try:
        result = AppraisalService.batch_update_appraisals(items, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量更新订单失败: {str(e)}")


@router.post("/result/add")
def batch_add_appraisal_results(
    request: AppraisalResultBatchRequest,
    session: Session = Depends(get_session)
):
    try:
        result = AppraisalService.batch_add_appraisal_results(request, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量添加鉴定结果失败: {str(e)}")