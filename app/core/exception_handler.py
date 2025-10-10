from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
import logging

from app.utils.response import error_response
from app.constants.response_codes import ResponseCode

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求参数验证异常
    """
    # 获取第一个错误信息
    first_error = exc.errors()[0] if exc.errors() else {}
    error_type = first_error.get('type', '')
    field_name = first_error.get('loc', [])[-1] if first_error.get('loc') else ''
    
    # 根据错误类型生成中文错误信息
    error_messages = {
        'string_pattern_mismatch': f'{field_name}格式不正确',
        'missing': f'{field_name}不能为空',
        'value_error': f'{field_name}值错误',
        'type_error': f'{field_name}类型错误',
        'greater_than_equal': f'{field_name}必须大于等于指定值',
        'less_than_equal': f'{field_name}必须小于等于指定值',
    }
    
    # 特殊处理手机号验证
    if field_name == 'userPhone' and error_type == 'string_pattern_mismatch':
        message = '手机号格式不正确，请输入有效的11位手机号'
    else:
        message = error_messages.get(error_type, f'{field_name}参数验证失败')
    
    return JSONResponse(
        status_code=400,
        content=error_response(
            code=ResponseCode.FAILURE,
            message=message
        )
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else error_response(
            code=ResponseCode.FAILURE,
            message=str(exc.detail)
        )
    )


async def starlette_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            code=ResponseCode.FAILURE,
            message=exc.detail
        )
    )


async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content=error_response(
            code=ResponseCode.FAILURE,
            message="服务器内部错误"
        )
    )