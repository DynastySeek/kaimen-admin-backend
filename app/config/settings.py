"""
应用设置配置
"""

# JWT 配置
SECRET_KEY = "your_secret_key_here"  # 建议使用安全生成的随机字符串
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 7200  # 2小时
