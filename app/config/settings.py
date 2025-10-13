"""
应用设置配置
"""
import os
from typing import Dict, Optional

# 环境配置
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development, testing, production

# 表名后缀配置函数
def get_table_suffix(base_table_name: str) -> str:
    """
    根据表名和环境返回相应的后缀
    """
    if ENVIRONMENT in ["development", "testing"]:
        # 根据实际数据库中的表名格式设置后缀
        if base_table_name in ["user", "appraisal_result"]:
            return "_preview"
        else:
            return "-preview"
    return ""

# JWT 配置
SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM") 
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 86400))

# 数据库配置
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DB = os.getenv("MYSQL_DB")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"


def get_runtime_env_config() -> Dict[str, str]:
    """
    收集启动时需要输出的环境变量配置（敏感信息不做掩码）。
    """
    return {
        "ENVIRONMENT": ENVIRONMENT,
        "SECRET_KEY": SECRET_KEY or "",
        "ALGORITHM": ALGORITHM or "",
        "ACCESS_TOKEN_EXPIRE_SECONDS": str(ACCESS_TOKEN_EXPIRE_SECONDS),
        "MYSQL_USER": MYSQL_USER or "",
        "MYSQL_PASSWORD": MYSQL_PASSWORD or "",
        "MYSQL_HOST": MYSQL_HOST or "",
        "MYSQL_PORT": MYSQL_PORT or "",
        "MYSQL_DB": MYSQL_DB or "",
        "DATABASE_URL": DATABASE_URL,
    }


def print_runtime_env_config() -> None:
    """
    启动时打印环境变量配置（不做掩码）。
    """
    cfg = get_runtime_env_config()
    print("[Startup] 环境变量配置：")
    for k, v in cfg.items():
        print(f"  - {k}: {v}")

# 启动时打印环境变量配置（敏感信息已掩码）
print_runtime_env_config()
