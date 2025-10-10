"""
FastAPI 基础应用
"""
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.core.exception_handler import (
    validation_exception_handler,
    http_exception_handler,
    starlette_exception_handler,
    general_exception_handler
)

# 创建 FastAPI 应用实例
app = FastAPI(
    title="开门管理后台",
    description="基于 FastAPI 构建的管理后台系统",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://admin.kaimen.site",
        "http://admin.kaimen.site", 
        "https://admin-test.kaimen.site",
        "http://admin-test.kaimen.site",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册全局异常处理器
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, starlette_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 注册API路由
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)