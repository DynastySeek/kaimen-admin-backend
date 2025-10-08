"""
统一响应格式模块
"""
from typing import Any, Optional, Dict, List, Union
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from ..constants.status_codes import BusinessCode, STATUS_CODE_MESSAGES


class ApiResponse(BaseModel):
    """API 统一响应格式"""
    code: int = BusinessCode.SUCCESS
    message: str = "操作成功"
    data: Optional[Any] = None
    timestamp: Optional[int] = None
    
    class Config:
        json_encoders = {
            # 可以在这里添加自定义编码器
        }


class PaginationResponse(BaseModel):
    """分页响应格式"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int
    
    @classmethod
    def create(cls, items: List[Any], total: int, page: int, page_size: int):
        """创建分页响应"""
        pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages
        )


def success_response(
    data: Any = None,
    message: str = "操作成功",
    code: int = BusinessCode.SUCCESS
) -> JSONResponse:
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        code: 业务状态码
    
    Returns:
        JSONResponse: JSON 响应
    """
    import time
    response_data = ApiResponse(
        code=code,
        message=message,
        data=data,
        timestamp=int(time.time())
    )
    return JSONResponse(
        status_code=200,
        content=response_data.dict()
    )


def error_response(
    code: int = BusinessCode.FAILED,
    message: Optional[str] = None,
    data: Any = None,
    status_code: int = 400
) -> JSONResponse:
    """
    错误响应
    
    Args:
        code: 业务状态码
        message: 错误消息
        data: 响应数据
        status_code: HTTP 状态码
    
    Returns:
        JSONResponse: JSON 响应
    """
    import time
    if message is None:
        message = STATUS_CODE_MESSAGES.get(code, "操作失败")
    
    response_data = ApiResponse(
        code=code,
        message=message,
        data=data,
        timestamp=int(time.time())
    )
    return JSONResponse(
        status_code=status_code,
        content=response_data.dict()
    )


def paginated_response(
    items: List[Any],
    total: int,
    page: int,
    page_size: int,
    message: str = "查询成功"
) -> JSONResponse:
    """
    分页响应
    
    Args:
        items: 数据列表
        total: 总数量
        page: 当前页码
        page_size: 每页大小
        message: 响应消息
    
    Returns:
        JSONResponse: JSON 响应
    """
    pagination_data = PaginationResponse.create(items, total, page, page_size)
    return success_response(data=pagination_data.dict(), message=message)