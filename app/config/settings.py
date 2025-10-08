"""
应用设置配置
"""

# JWT 配置
SECRET_KEY = "kaimen_admin"  # 建议使用安全生成的随机字符串
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 86400  # 24小时

# 数据库配置
MYSQL_USER = "kaimen"
MYSQL_PASSWORD = "7xK9#mQp2$vL8"
MYSQL_HOST = "sh-cynosdbmysql-grp-1cwincl8.sql.tencentcdb.com"
MYSQL_PORT = 28288
MYSQL_DB = "lowcode-3gkr3shu8224cfca"

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
