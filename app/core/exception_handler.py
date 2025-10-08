from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
import logging

from app.utils.response import error_response
from app.constants.response_codes import ResponseCode

logger = logging.getLogger(__name__)


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