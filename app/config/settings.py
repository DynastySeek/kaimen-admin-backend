"""
应用设置配置
"""
import os
from typing import Dict, Optional
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_file = BASE_DIR / ".env"

# 如果 .env 文件存在则加载
if env_file.exists():
    load_dotenv(env_file)
else:
    # 尝试加载其他环境配置文件
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        load_dotenv(BASE_DIR / ".env.prod")
    elif env == "testing":
        load_dotenv(BASE_DIR / ".env.test")

# 环境配置
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development, testing, production

# 表名后缀配置函数
def get_table_suffix(base_table_name: str) -> str:
    """
    根据表名和环境返回相应的后缀
    """
    if ENVIRONMENT in ["development", "testing"]:
        # 根据实际数据库中的表名格式设置后缀
        if base_table_name in ["user", "appraisal_result", "appraisal_buy", "appraisal_consignment"]:
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

# 腾讯云 COS 配置
COS_SECRET_ID = os.getenv("COS_SECRET_ID")
COS_SECRET_KEY = os.getenv("COS_SECRET_KEY")
COS_REGION = os.getenv("COS_REGION")
COS_BUCKET = os.getenv("COS_BUCKET")

# Redis 配置
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_USER = os.getenv("REDIS_USER")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Redis 连接 URL
REDIS_URL = f"redis://{REDIS_USER}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}" if REDIS_USER and REDIS_PASSWORD else f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# 腾讯云短信配置
TENCENT_CLOUD_SECRET_ID = os.getenv("TENCENT_CLOUD_SECRET_ID")
TENCENT_CLOUD_SECRET_KEY = os.getenv("TENCENT_CLOUD_SECRET_KEY")
SMS_SDK_APP_ID = os.getenv("SMS_SDK_APP_ID")
SMS_REGION = os.getenv("SMS_REGION", "ap-guangzhou")
SMS_SIGN_NAME = os.getenv("SMS_SIGN_NAME")

# 短信模板ID配置
SMS_TEMPLATE_STATUS_COMPLETE = "2532457"  # 真/假/驳回（订单已完成）
SMS_TEMPLATE_DOUBT = "2532458"  # 存疑/待完善
SMS_TEMPLATE_REJECTED = "2538861"  # 已退回

# 短信延迟发送配置
SMS_DELAY_SECONDS = int(os.getenv("SMS_DELAY_SECONDS", 300))  # 默认5分钟延迟


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
        "REDIS_HOST": REDIS_HOST or "",
        "REDIS_PORT": str(REDIS_PORT),
        "REDIS_USER": REDIS_USER or "",
        "REDIS_PASSWORD": REDIS_PASSWORD or "",
        "REDIS_DB": str(REDIS_DB),
        "REDIS_URL": REDIS_URL,
        "COS_SECRET_ID": COS_SECRET_ID or "",
        "COS_SECRET_KEY": COS_SECRET_KEY or "",
        "COS_REGION": COS_REGION or "",
        "COS_BUCKET": COS_BUCKET or "",
        "REDIS_HOST": REDIS_HOST or "",
        "REDIS_PORT": str(REDIS_PORT),
        "REDIS_USER": REDIS_USER or "",
        "REDIS_PASSWORD": REDIS_PASSWORD or "",
        "REDIS_DB": str(REDIS_DB),
        "REDIS_URL": REDIS_URL,
    }


def print_runtime_env_config() -> None:
    """
    启动时打印环境变量配置（不做掩码）。
    """
    # 计算北京时间启动时间
    startup_dt = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))
    startup_time_str = startup_dt.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[Startup] 启动时间（北京时间）：{startup_time_str}")

    cfg = get_runtime_env_config()
    print("[Startup] 环境变量配置：")
    for k, v in cfg.items():
        print(f"  - {k}: {v}")

# 启动时打印环境变量配置（敏感信息已掩码）
print_runtime_env_config()
