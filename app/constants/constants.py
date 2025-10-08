"""
常量定义模块
"""

# 分页相关常量
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# 缓存相关常量
CACHE_EXPIRE_TIME = 3600  # 1小时
SHORT_CACHE_EXPIRE_TIME = 300  # 5分钟
LONG_CACHE_EXPIRE_TIME = 86400  # 24小时

# 文件上传相关常量
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt"}

# JWT 相关常量
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# 密码相关常量
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

# 用户相关常量
MAX_USERNAME_LENGTH = 50
MAX_EMAIL_LENGTH = 255
MAX_PHONE_LENGTH = 20

# API 相关常量
API_PREFIX = "/api"
API_VERSION = "v1"

# 数据库相关常量
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_RECYCLE = 3600

# 日志相关常量
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 业务相关常量
DEFAULT_AVATAR = "/static/images/default_avatar.png"
SYSTEM_USER_ID = 0