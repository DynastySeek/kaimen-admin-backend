"""
安全相关工具函数
"""
import secrets
import string
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from ..config.env import get_settings

settings = get_settings()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_random_string(length: int = 32) -> str:
    """
    生成随机字符串
    
    Args:
        length: 字符串长度
        
    Returns:
        str: 随机字符串
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_password_hash(password: str) -> str:
    """
    生成密码哈希值
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希密码
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        bool: 验证结果
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None,
    secret_key: Optional[str] = None,
    algorithm: str = "HS256"
) -> str:
    """
    创建JWT令牌
    
    Args:
        data: 令牌数据
        expires_delta: 过期时间增量
        secret_key: 密钥
        algorithm: 算法
        
    Returns:
        str: JWT令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    
    key = secret_key or settings.secret_key
    encoded_jwt = jwt.encode(to_encode, key, algorithm=algorithm)
    return encoded_jwt


def decode_jwt_token(
    token: str, 
    secret_key: Optional[str] = None,
    algorithms: Optional[list] = None
) -> dict:
    """
    解码JWT令牌
    
    Args:
        token: JWT令牌
        secret_key: 密钥
        algorithms: 算法列表
        
    Returns:
        dict: 令牌载荷
        
    Raises:
        JWTError: 令牌解码失败
    """
    key = secret_key or settings.secret_key
    algs = algorithms or [settings.algorithm]
    
    try:
        payload = jwt.decode(token, key, algorithms=algs)
        return payload
    except JWTError as e:
        raise JWTError(f"Token decode failed: {str(e)}")


def is_strong_password(password: str) -> bool:
    """
    检查密码强度
    
    Args:
        password: 密码
        
    Returns:
        bool: 是否为强密码
    """
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    return sum([has_upper, has_lower, has_digit, has_special]) >= 3


def generate_verification_code(length: int = 6) -> str:
    """
    生成验证码
    
    Args:
        length: 验证码长度
        
    Returns:
        str: 验证码
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def mask_email(email: str) -> str:
    """
    邮箱脱敏
    
    Args:
        email: 邮箱地址
        
    Returns:
        str: 脱敏后的邮箱
    """
    if '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked_local = local
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """
    手机号脱敏
    
    Args:
        phone: 手机号
        
    Returns:
        str: 脱敏后的手机号
    """
    if len(phone) < 7:
        return phone
    
    return phone[:3] + '*' * (len(phone) - 6) + phone[-3:]


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除危险字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 清理后的文件名
    """
    # 移除路径分隔符和其他危险字符
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    clean_name = filename
    
    for char in dangerous_chars:
        clean_name = clean_name.replace(char, '_')
    
    # 限制文件名长度
    if len(clean_name) > 255:
        name, ext = clean_name.rsplit('.', 1) if '.' in clean_name else (clean_name, '')
        max_name_length = 255 - len(ext) - 1 if ext else 255
        clean_name = name[:max_name_length] + ('.' + ext if ext else '')
    
    return clean_name