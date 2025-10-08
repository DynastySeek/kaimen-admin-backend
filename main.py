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


@app.get("/", summary="根路径")
async def root():
    """
    根路径接口
    
    Returns:
        dict: 欢迎信息
    """
    return {"message": "欢迎使用开门管理后台 API"}


@app.get("/health", summary="健康检查")
async def health_check():
    """
    健康检查接口
    
    Returns:
        dict: 健康状态
    """
    return {"status": "healthy", "message": "服务运行正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)