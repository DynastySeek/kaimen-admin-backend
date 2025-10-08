"""
API 依赖模块 - 已移除数据库相关依赖
"""
from fastapi import Depends
from ..core.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    get_pagination_params,
    get_optional_user,
    PaginationParams
)

# 注意：数据库相关依赖已移除
# 如需使用云数据库，请重新实现相关依赖

# 重新导出依赖，方便在路由中使用
__all__ = [
    # "get_db",  # 已移除数据库依赖
    "get_current_user",
    "get_current_active_user", 
    "get_current_admin_user",
    "get_pagination_params",
    "get_optional_user",
    "PaginationParams"
]