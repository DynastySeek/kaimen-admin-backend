"""
鉴宝求购API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import Optional

from app.services.appraisal_buy import AppraisalBuyService
from app.utils.db import get_session
from app.utils.response import success_response

router = APIRouter()


@router.get("/list")
def get_appraisal_buy_list(
    page: int = Query(1, ge=1, description="页码"),
    pageSize: int = Query(20, ge=1, le=100, description="每页数量"),
    id: Optional[str] = Query(None, description="求购ID"),
    buyer_type: Optional[str] = Query(None, description="求购类型"),
    desc: Optional[str] = Query(None, description="描述"),
    minPrice: Optional[float] = Query(None, description="最低价格"),
    maxPrice: Optional[float] = Query(None, description="最高价格"),
    userPhone: Optional[str] = Query(None, regex=r'^1[3-9]\d{9}$', description="用户登录授权手机号，必须是11位有效手机号"),
    phone: Optional[str] = Query(None, description="用户填写联系方式"),
    createStartTime: Optional[str] = None,
    createEndTime: Optional[str] = None,
    session: Session = Depends(get_session)
):
    try:
        data = AppraisalBuyService.get_appraisal_buy_list(
            page=page,
            pageSize=pageSize,
            id=id,
            buyer_type=buyer_type,
            desc=desc,
            minPrice=minPrice,
            maxPrice=maxPrice,
            userPhone=userPhone,
            phone=phone,
            createStartTime=createStartTime,
            createEndTime=createEndTime,
            session=session
        )
        
        return success_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")