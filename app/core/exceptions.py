"""
自定义异常类和全局异常处理器
"""
from typing import Any, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR
)
# 注意：SQLAlchemy相关导入已移除
from .response import error_response
from ..constants.status_codes import BusinessCode


class BusinessException(Exception):
    """业务异常基类"""
    
    def __init__(
        self,
        code: int = BusinessCode.FAILED,
        message: Optional[str] = None,
        data: Any = None
    ):
        self.code = code
        self.message = message or STATUS_CODE_MESSAGES.get(code, "操作失败")
        self.data = data
        super().__init__(self.message)


class UserException(BusinessException):
    """用户相关异常"""
    pass


class AuthException(BusinessException):
    """认证相关异常"""
    pass


class PermissionException(BusinessException):
    """权限相关异常"""
    pass


class DataException(BusinessException):
    """数据相关异常"""
    pass


class FileException(BusinessException):
    """文件相关异常"""
    pass


class SystemException(BusinessException):
    """系统相关异常"""
    pass


async def business_exception_handler(request: Request, exc: BusinessException) -> JSONResponse:
    """
    业务异常处理器
    
    Args:
        request: 请求对象
        exc: 业务异常
    
    Returns:
        JSONResponse: 错误响应
    """
    return error_response(
        code=exc.code,
        message=exc.message,
        data=exc.data,
        status_code=400
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    HTTP 异常处理器
    
    Args:
        request: 请求对象
        exc: HTTP 异常
    
    Returns:
        JSONResponse: 错误响应
    """
    return error_response(
        code=BusinessCode.FAILED,
        message=exc.detail,
        status_code=exc.status_code
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    参数验证异常处理器
    
    Args:
        request: 请求对象
        exc: 参数验证异常
    
    Returns:
        JSONResponse: 错误响应
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    return error_response(
        code=BusinessCode.INVALID_PARAMETER,
        message="参数验证失败: " + "; ".join(errors),
        data=exc.errors(),
        status_code=422
    )


# 注意：SQLAlchemy异常处理器已移除
# 如需使用云数据库，请根据实际情况重新实现数据库异常处理


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    通用异常处理器
    
    Args:
        request: 请求对象
        exc: 异常
    
    Returns:
        JSONResponse: 错误响应
    """
    return error_response(
        code=BusinessCode.SYSTEM_ERROR,
        message="系统内部错误",
        status_code=HTTP_500_INTERNAL_SERVER_ERROR
    )