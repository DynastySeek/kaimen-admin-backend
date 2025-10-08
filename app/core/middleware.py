"""
认证中间件
"""
from typing import Optional, Callable
from fastapi import Request, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param

from app.services.auth import verify_token
from app.services.user import get_user_by_id
from app.utils.response import ResponseCode


class AuthMiddleware:
    """认证中间件类"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # 检查是否需要认证的路径
            if self._should_authenticate(request.url.path):
                user = await self._authenticate_request(request)
                if user:
                    # 将用户信息添加到请求状态中
                    scope["state"] = getattr(scope, "state", {})
                    scope["state"]["current_user"] = user
        
        await self.app(scope, receive, send)
    
    def _should_authenticate(self, path: str) -> bool:
        """
        判断路径是否需要认证
        
        Args:
            path: 请求路径
            
        Returns:
            bool: 是否需要认证
        """
        # 不需要认证的路径
        public_paths = [
            "/",
            "/health",
            "/api/auth/login",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        
        return path not in public_paths and not path.startswith("/static")
    
    async def _authenticate_request(self, request: Request) -> Optional[dict]:
        """
        认证请求
        
        Args:
            request: FastAPI请求对象
            
        Returns:
            Optional[dict]: 用户信息或None
        """
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        
        scheme, token = get_authorization_scheme_param(authorization)
        if scheme.lower() != "bearer":
            return None
        
        user_id = verify_token(token)
        if not user_id:
            return None
        
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return None
        
        user = get_user_by_id(user_id)
        if not user:
            return None
        
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "nickname": user.nickname,
            "phone": user.phone,
            "avatar": user.avatar
        }


def require_auth(optional: bool = False) -> Callable:
    """
    认证装饰器
    
    Args:
        optional: 是否可选认证
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(request: Request, *args, **kwargs):
            # 从请求状态中获取用户信息
            current_user = getattr(request.state, "current_user", None)
            
            if not current_user and not optional:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "code": ResponseCode.UNAUTHORIZED,
                        "message": "认证失败",
                        "data": None
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 将用户信息添加到函数参数中
            kwargs["current_user"] = current_user
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator