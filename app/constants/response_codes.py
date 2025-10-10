"""
响应码常量定义
"""


class ResponseCode:
    """响应状态码常量"""
    # 业务响应码
    SUCCESS = 0          # 成功
    FAILURE = -1         # 失败
    
    # HTTP状态码
    HTTP_SUCCESS = 200   # HTTP成功
    HTTP_ERROR = 500     # HTTP服务器错误
    
    # 认证和授权相关
    UNAUTHORIZED = 401   # 未授权
    FORBIDDEN = 403      # 禁止访问


class ResponseMessage:
    """响应消息常量"""
    SUCCESS = "操作成功"
    FAILURE = "操作失败"
    INTERNAL_ERROR = "服务器内部错误"
    BAD_REQUEST = "请求参数错误"
    UNAUTHORIZED = "未授权访问"
    FORBIDDEN = "禁止访问"
    NOT_FOUND = "资源不存在"