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
    id: Optional[str] = Query(None, description="求购ID"),
    type: Optional[str] = Query(None, description="类目"),
    desc: Optional[str] = Query(None, description="描述"),
    minExpectedPrice: Optional[float] = Query(None, description="最低心理价位"),
    maxExpectedPrice: Optional[float] = Query(None, description="最高心理价位"),
    userPhone: Optional[str] = Query(None, regex=r'^1[3-9]\d{9}$', description="用户登录授权手机号，必须是11位有效手机号"),
    phone: Optional[str] = Query(None, description="用户填写联系方式"),
    wechatId: Optional[str] = Query(None, description="微信id"),
    createStartTime: Optional[str] = None,
    createEndTime: Optional[str] = None,
    session: Session = Depends(get_session)
):
    try:
        data = AppraisalConsignmentService.get_appraisal_consignment_list(
            page=page,
            pageSize=pageSize,
            id=id,
            type=type,
            desc=desc,
            minExpectedPrice=minExpectedPrice,
            maxExpectedPrice=maxExpectedPrice,
            userPhone=userPhone,
            phone=phone,
            wechatId=wechatId,
            createStartTime=createStartTime,
            createEndTime=createEndTime,
            session=session
        )
        
        return success_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")