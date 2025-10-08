"""
依赖注入模块 - 已移除数据库相关依赖
"""
from typing import Optional, Generator
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..constants.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from ..constants.status_codes import BusinessCode
from .exceptions import AuthException

# 注意：数据库相关依赖已移除
# 如需使用云数据库，请重新实现相关依赖

# JWT 认证
security = HTTPBearer()


class PaginationParams:
    """分页参数类"""
    
    def __init__(
        self,
        page: int = Query(DEFAULT_PAGE, ge=1, description="页码"),
        page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页数量")
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size


def get_pagination_params(
    page: int = Query(DEFAULT_PAGE, ge=1, description="页码"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页数量")
) -> PaginationParams:
    """
    获取分页参数
    
    Args:
        page: 页码
        page_size: 每页数量
    
    Returns:
        PaginationParams: 分页参数对象
    """
    return PaginationParams(page=page, page_size=page_size)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    获取当前用户 - 已禁用
    
    注意：此函数已被禁用，因为项目不再使用本地数据库
    如需使用云数据库，请重新实现此函数
    
    Args:
        credentials: JWT 凭证
    
    Raises:
        NotImplementedError: 功能已被移除
    """
    raise NotImplementedError("用户认证功能已被移除，请使用云服务重新实现")


def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """
    获取当前活跃用户 - 已禁用
    
    注意：此函数已被禁用，因为项目不再使用本地数据库
    如需使用云数据库，请重新实现此函数
    
    Args:
        current_user: 当前用户
    
    Raises:
        NotImplementedError: 功能已被移除
    """
    raise NotImplementedError("用户认证功能已被移除，请使用云服务重新实现")


def get_current_admin_user(
    current_user = Depends(get_current_active_user)
):
    """
    获取当前管理员用户 - 已禁用
    
    注意：此函数已被禁用，因为项目不再使用本地数据库
    如需使用云数据库，请重新实现此函数
    
    Args:
        current_user: 当前用户
    
    Raises:
        NotImplementedError: 功能已被移除
    """
    raise NotImplementedError("管理员认证功能已被移除，请使用云服务重新实现")


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    获取可选用户 - 已禁用
    
    注意：此函数已被禁用，因为项目不再使用本地数据库
    如需使用云数据库，请重新实现此函数
    
    Args:
        credentials: JWT 凭证（可选）
    
    Returns:
        None: 始终返回None
    """
    return None