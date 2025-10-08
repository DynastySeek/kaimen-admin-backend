"""
状态码常量定义模块
"""

# HTTP 状态码
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_500_INTERNAL_SERVER_ERROR = 500

# 业务状态码
class BusinessCode:
    """业务状态码"""
    SUCCESS = 0
    FAILED = -1
    
    # 用户相关 1000-1999
    USER_NOT_FOUND = 1001
    USER_ALREADY_EXISTS = 1002
    USER_DISABLED = 1003
    INVALID_CREDENTIALS = 1004
    PASSWORD_TOO_WEAK = 1005
    
    # 权限相关 2000-2999
    PERMISSION_DENIED = 2001
    TOKEN_EXPIRED = 2002
    TOKEN_INVALID = 2003
    INSUFFICIENT_PERMISSIONS = 2004
    
    # 参数相关 3000-3999
    INVALID_PARAMETER = 3001
    MISSING_PARAMETER = 3002
    PARAMETER_TYPE_ERROR = 3003
    
    # 数据相关 4000-4999
    DATA_NOT_FOUND = 4001
    DATA_ALREADY_EXISTS = 4002
    DATA_CONFLICT = 4003
    DATA_INTEGRITY_ERROR = 4004
    
    # 文件相关 5000-5999
    FILE_NOT_FOUND = 5001
    FILE_TOO_LARGE = 5002
    FILE_TYPE_NOT_ALLOWED = 5003
    FILE_UPLOAD_FAILED = 5004
    
    # 系统相关 9000-9999
    SYSTEM_ERROR = 9001
    DATABASE_ERROR = 9002
    NETWORK_ERROR = 9003
    SERVICE_UNAVAILABLE = 9004


# 状态码消息映射
STATUS_CODE_MESSAGES = {
    BusinessCode.SUCCESS: "操作成功",
    BusinessCode.FAILED: "操作失败",
    
    # 用户相关
    BusinessCode.USER_NOT_FOUND: "用户不存在",
    BusinessCode.USER_ALREADY_EXISTS: "用户已存在",
    BusinessCode.USER_DISABLED: "用户已被禁用",
    BusinessCode.INVALID_CREDENTIALS: "用户名或密码错误",
    BusinessCode.PASSWORD_TOO_WEAK: "密码强度不够",
    
    # 权限相关
    BusinessCode.PERMISSION_DENIED: "权限不足",
    BusinessCode.TOKEN_EXPIRED: "令牌已过期",
    BusinessCode.TOKEN_INVALID: "令牌无效",
    BusinessCode.INSUFFICIENT_PERMISSIONS: "权限不足",
    
    # 参数相关
    BusinessCode.INVALID_PARAMETER: "参数无效",
    BusinessCode.MISSING_PARAMETER: "缺少必要参数",
    BusinessCode.PARAMETER_TYPE_ERROR: "参数类型错误",
    
    # 数据相关
    BusinessCode.DATA_NOT_FOUND: "数据不存在",
    BusinessCode.DATA_ALREADY_EXISTS: "数据已存在",
    BusinessCode.DATA_CONFLICT: "数据冲突",
    BusinessCode.DATA_INTEGRITY_ERROR: "数据完整性错误",
    
    # 文件相关
    BusinessCode.FILE_NOT_FOUND: "文件不存在",
    BusinessCode.FILE_TOO_LARGE: "文件过大",
    BusinessCode.FILE_TYPE_NOT_ALLOWED: "文件类型不允许",
    BusinessCode.FILE_UPLOAD_FAILED: "文件上传失败",
    
    # 系统相关
    BusinessCode.SYSTEM_ERROR: "系统错误",
    BusinessCode.DATABASE_ERROR: "数据库错误",
    BusinessCode.NETWORK_ERROR: "网络错误",
    BusinessCode.SERVICE_UNAVAILABLE: "服务不可用",
}