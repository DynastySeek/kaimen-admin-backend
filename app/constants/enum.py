from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class AppraisalResult(str, Enum):
    """鉴定结果枚举"""
    AUTHENTIC = "1"  # 真
    FAKE = "2"  # 假
    DOUBT = "3"  # 存疑
    REJECTED = "4"  # 驳回


class PubStatus(str, Enum):
    """发布状态枚举"""
    TO_PUBLISH = "1"  # 待发布
    PUBLISHED = "2"  # 已发布
    OFFLINE = "3"  # 已下线


class AppraisalStatus(int, Enum):
    """鉴定状态枚举"""
    PENDING_APPRAISAL = 1  # 待鉴定
    IN_PROGRESS = 2  # 鉴定中
    COMPLETED = 3  # 已完结
    PENDING_COMPLETION = 4  # 待完善
    REJECTED = 5  # 已退回
    CANCELLED = 6  # 已取消


class AppraisalClass(int, Enum):
    """鉴定类别枚举"""
    YIN_YUAN = 1  # 银元
    GU_QIAN = 2  # 古钱
    ZA_XIANG = 4  # 杂项
    ZHI_BI = 5  # 纸币

