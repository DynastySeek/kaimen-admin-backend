"""
鉴定相关的数据模式
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BatchDetailRequest(BaseModel):
    """批量详情请求模式"""
    ids: List[str]


class LatestAppraisalData(BaseModel):
    """最新鉴定数据模式"""
    appraisal_id: str
    result: str
    notes: str
    user_id: Optional[int] = None
    created_at: datetime


class AppraisalDetail(BaseModel):
    """鉴定详情模式"""
    appraisal_id: str
    title: str
    desc: str
    appraisal_status: str
    first_class: str
    create_time: int
    result: str = ""
    notes: str = ""
    user_id: Optional[int] = None


class BatchDetailResponse(BaseModel):
    """批量详情响应模式"""
    code: int = 200
    message: str = "查询成功"
    data: List[AppraisalDetail]


class BatchUpdateItem(BaseModel):
    """批量更新项模式"""
    appraisalId: str
    appraisalClass: Optional[str] = None
    appraisalResult: Optional[int] = None
    comment: Optional[str] = None


class BatchUpdateRequest(BaseModel):
    """批量更新请求模式"""
    items: List[BatchUpdateItem]


class BatchUpdateResult(BaseModel):
    """批量更新结果模式"""
    success_count: int
    failed_count: int
    failed_items: List[str]


class BatchUpdateResponse(BaseModel):
    """批量更新响应模式"""
    code: int = 200
    message: str = "批量修改完成"
    data: BatchUpdateResult


class AppraisalUpdateItem(BaseModel):
    """鉴定更新项模式"""
    id: str
    appraisal_status: Optional[int] = None
    appraisal_class: Optional[str] = None


class OrderUpdateResult(BaseModel):
    """订单更新结果模式"""
    appraisal_id: int
    success: bool
    message: str


class OrderUpdateResponse(BaseModel):
    """订单更新响应模式"""
    code: int = 200
    message: str = "批量更新完成"
    data: List[OrderUpdateResult]


class FailedItem(BaseModel):
    """失败项模式"""
    appraisal_id: str
    reason: str


class BatchAddResultData(BaseModel):
    """批量添加结果数据模式"""
    success_count: int
    failed_count: int
    failed_items: List[FailedItem]


class BatchAddResultResponse(BaseModel):
    """批量添加结果响应模式"""
    code: int = 200
    message: str = "批量修改完成"
    data: BatchAddResultData


class AppraisalResultItem(BaseModel):
    """鉴定结果项模式"""
    appraisalId: str
    appraisalResult: str
    comment: Optional[str] = None
    reasons: Optional[List[str]] = []


class AppraisalResultBatchRequest(BaseModel):
    """鉴定结果批量请求模式"""
    items: List[AppraisalResultItem]