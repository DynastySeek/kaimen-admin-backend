"""
统一响应格式处理工具
"""
from typing import Any, Optional
from fastapi import HTTPException
from fastapi.responses import JSONResponse


class ResponseCode:
    """响应状态码"""
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500


def success_response(data: Any = None, message: str = "操作成功") -> dict:
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        
    Returns:
        dict: 统一格式的成功响应
    """
    return {
        "code": ResponseCode.SUCCESS,
        "message": message,
        "data": data
    }


def error_response(code: int = ResponseCode.INTERNAL_ERROR, message: str = "操作失败", data: Any = None) -> dict:
    """
    错误响应
    
    Args:
        code: 错误码
        message: 错误消息
        data: 错误数据
        
    Returns:
        dict: 统一格式的错误响应
    """
    return {
        "code": code,
        "message": message,
        "data": data
    }


def raise_http_error(code: int = ResponseCode.INTERNAL_ERROR, message: str = "操作失败", data: Any = None):
    """
    抛出HTTP错误
    
    Args:
        code: 错误码
        message: 错误消息
        data: 错误数据
        
    Raises:
        HTTPException: HTTP异常
    """
    raise HTTPException(
        status_code=code,
        detail=error_response(code, message, data)
    )


def json_response(data: Any = None, message: str = "操作成功", code: int = ResponseCode.SUCCESS) -> JSONResponse:
    """
    JSON响应
    
    Args:
        data: 响应数据
        message: 响应消息
        code: 响应码
        
    Returns:
        JSONResponse: JSON响应对象
    """
    return JSONResponse(
        status_code=200,
        content={
            "code": code,
            "message": message,
            "data": data
        }
    )