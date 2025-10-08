"""
环境配置管理模块
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    PROJECT_NAME: str = "Kaimen Admin Backend"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "prod"  # test, prod
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置已移除
    # DATABASE_URL: Optional[str] = None
    
    # JWT 配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS 配置
    CORS_ORIGINS: List[str] = ["*"]
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        case_sensitive = True
        
    @property
    def env_file(self) -> str:
        """根据环境返回对应的环境变量文件"""
        if self.ENVIRONMENT == "test":
            return ".env.test"
        return ".env.prod"


def get_settings() -> Settings:
    """
    获取应用配置
    根据环境变量 ENVIRONMENT 加载对应配置
    """
    env = os.getenv("ENVIRONMENT", "prod")
    if env == "test":
        return Settings(_env_file=".env.test")
    return Settings(_env_file=".env.prod")


# 全局配置实例
settings = get_settings()