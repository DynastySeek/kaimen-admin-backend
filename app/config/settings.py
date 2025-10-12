"""
应用设置配置
"""
import os

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
SECRET_KEY = os.getenv("SECRET_KEY") ## "kaimen_admin"  # 建议使用安全生成的随机字符串

ALGORITHM = os.getenv("ALGORITHM") 
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 86400))

# 数据库配置
MYSQL_USER = os.getenv("MYSQL_USER") # "kaimen"
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")  # "7xK9#mQp2$vL8"
MYSQL_HOST = os.getenv("MYSQL_HOST") # "sh-cynosdbmysql-grp-1cwincl8.sql.tencentcdb.com"
MYSQL_PORT = os.getenv("MYSQL_PORT") # 28288
MYSQL_DB = os.getenv("MYSQL_DB") # "lowcode-3gkr3shu8224cfca"

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
