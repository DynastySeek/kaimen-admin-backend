"""
FastAPI 基础应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router

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

# 注册API路由
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)