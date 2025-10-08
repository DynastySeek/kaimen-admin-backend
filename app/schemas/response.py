"""
响应 Schema 模块
"""
from typing import Any, Optional, List, Generic, TypeVar
from pydantic import BaseModel, Field
from .base import BaseSchema

T = TypeVar('T')


class ApiResponseSchema(BaseSchema, Generic[T]):
    """API 响应 Schema"""
    code: int = Field(0, description="业务状态码")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    timestamp: Optional[int] = Field(None, description="时间戳")


class PaginationResponseSchema(BaseSchema, Generic[T]):
    """分页响应 Schema"""
    items: List[T] = Field([], description="数据列表")
    total: int = Field(0, description="总数量")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(20, description="每页大小")
    pages: int = Field(0, description="总页数")


class SuccessResponseSchema(BaseSchema):
    """成功响应 Schema"""
    message: str = Field("操作成功", description="成功消息")


class ErrorResponseSchema(BaseSchema):
    """错误响应 Schema"""
    code: int = Field(-1, description="错误码")
    message: str = Field("操作失败", description="错误消息")
    data: Optional[Any] = Field(None, description="错误详情")