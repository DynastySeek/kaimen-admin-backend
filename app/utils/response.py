"""
统一响应格式处理工具
"""
from typing import Any, Optional
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.constants.response_codes import ResponseCode, ResponseMessage


def success_response(data: Any = None, message: str = ResponseMessage.SUCCESS) -> dict:
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
        "data": data,
        "success": True
    }


def error_response(code: int = ResponseCode.FAILURE, message: str = ResponseMessage.FAILURE, data: Any = None) -> dict:
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
        "data": data,
        "success": False
    }


def raise_http_error(code: int = ResponseCode.FAILURE, message: str = ResponseMessage.FAILURE, data: Any = None):
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
        status_code=ResponseCode.HTTP_ERROR,
        detail=error_response(code, message, data)
    )


def json_response(data: Any = None, message: str = ResponseMessage.SUCCESS, code: int = ResponseCode.SUCCESS) -> JSONResponse:
    """
    JSON响应
    
    Args:
        data: 响应数据
        message: 响应消息
        code: 响应码
        
    Returns:
        JSONResponse: JSON响应对象
    """
    success = code == ResponseCode.SUCCESS
    status_code = ResponseCode.HTTP_SUCCESS if success else ResponseCode.HTTP_ERROR
    
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "data": data,
            "success": success
        }
    )