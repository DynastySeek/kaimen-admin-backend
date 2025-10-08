"""
开门管理后台 - 主应用入口文件
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.env import get_settings
from app.core.middleware import setup_middlewares
from app.core.exceptions import (
    business_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.core.exceptions import (
    BusinessException,
    HTTPException,
    RequestValidationError
)
from app.api.router import api_router

# 获取配置
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    Args:
        app: FastAPI应用实例
    """
    # 启动时执行
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} 正在启动...")
    
    # 注意：数据库初始化代码已移除
    # 如需使用云数据库，请在此处添加相应的初始化代码
    
    print(f"🌍 环境: {settings.ENVIRONMENT}")
    print(f"🔧 调试模式: {settings.DEBUG}")
    print(f"🏠 服务地址: http://{settings.HOST}:{settings.PORT}")
    
    yield
    
    # 关闭时执行
    print("👋 应用正在关闭...")


def create_app() -> FastAPI:
    """
    创建 FastAPI 应用实例
    
    Returns:
        FastAPI: 应用实例
    """
    # 创建应用实例
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="开门管理后台 API",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # 设置中间件
    setup_middlewares(app)
    
    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册异常处理器
    app.add_exception_handler(BusinessException, business_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    # 注意：SQLAlchemy异常处理器已移除
    app.add_exception_handler(Exception, general_exception_handler)
    
    # 注册路由
    app.include_router(api_router, prefix="/api")
    
    # 健康检查端点
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT
        }
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )