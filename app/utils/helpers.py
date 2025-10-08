"""
通用工具函数
"""
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal
import json


def generate_uuid() -> str:
    """
    生成UUID
    
    Returns:
        str: UUID字符串
    """
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """
    生成短ID
    
    Args:
        length: ID长度
        
    Returns:
        str: 短ID
    """
    return str(uuid.uuid4()).replace('-', '')[:length]


def is_valid_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        bool: 是否有效
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_phone(phone: str) -> bool:
    """
    验证手机号格式（中国大陆）
    
    Args:
        phone: 手机号
        
    Returns:
        bool: 是否有效
    """
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间
    
    Args:
        dt: 日期时间对象
        format_str: 格式字符串
        
    Returns:
        str: 格式化后的字符串
    """
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    解析日期时间字符串
    
    Args:
        dt_str: 日期时间字符串
        format_str: 格式字符串
        
    Returns:
        datetime: 日期时间对象
    """
    return datetime.strptime(dt_str, format_str)


def get_current_timestamp() -> int:
    """
    获取当前时间戳（秒）
    
    Returns:
        int: 时间戳
    """
    return int(datetime.now().timestamp())


def get_current_timestamp_ms() -> int:
    """
    获取当前时间戳（毫秒）
    
    Returns:
        int: 时间戳
    """
    return int(datetime.now().timestamp() * 1000)


def timestamp_to_datetime(timestamp: Union[int, float]) -> datetime:
    """
    时间戳转日期时间
    
    Args:
        timestamp: 时间戳
        
    Returns:
        datetime: 日期时间对象
    """
    return datetime.fromtimestamp(timestamp)


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    安全的JSON解析
    
    Args:
        json_str: JSON字符串
        default: 默认值
        
    Returns:
        Any: 解析结果
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    安全的JSON序列化
    
    Args:
        obj: 要序列化的对象
        default: 默认值
        
    Returns:
        str: JSON字符串
    """
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return default


def deep_merge_dict(dict1: Dict, dict2: Dict) -> Dict:
    """
    深度合并字典
    
    Args:
        dict1: 字典1
        dict2: 字典2
        
    Returns:
        Dict: 合并后的字典
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dict(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """
    扁平化字典
    
    Args:
        d: 字典
        parent_key: 父键
        sep: 分隔符
        
    Returns:
        Dict: 扁平化后的字典
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    将列表分块
    
    Args:
        lst: 列表
        chunk_size: 块大小
        
    Returns:
        List[List]: 分块后的列表
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_duplicates(lst: List, key: Optional[str] = None) -> List:
    """
    去除列表重复项
    
    Args:
        lst: 列表
        key: 用于比较的键（针对字典列表）
        
    Returns:
        List: 去重后的列表
    """
    if not lst:
        return lst
    
    if key is None:
        return list(dict.fromkeys(lst))
    
    seen = set()
    result = []
    for item in lst:
        if isinstance(item, dict) and key in item:
            if item[key] not in seen:
                seen.add(item[key])
                result.append(item)
        else:
            if item not in seen:
                seen.add(item)
                result.append(item)
    
    return result


def calculate_pagination(total: int, page: int, page_size: int) -> Dict[str, int]:
    """
    计算分页信息
    
    Args:
        total: 总数
        page: 当前页
        page_size: 每页大小
        
    Returns:
        Dict[str, int]: 分页信息
    """
    total_pages = (total + page_size - 1) // page_size
    has_prev = page > 1
    has_next = page < total_pages
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_prev": has_prev,
        "has_next": has_next,
        "prev_page": page - 1 if has_prev else None,
        "next_page": page + 1 if has_next else None
    }


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
        
    Returns:
        str: 格式化后的大小
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断字符串
    
    Args:
        text: 原始字符串
        max_length: 最大长度
        suffix: 后缀
        
    Returns:
        str: 截断后的字符串
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix