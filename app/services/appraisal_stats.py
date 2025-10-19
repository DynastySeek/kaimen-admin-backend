"""
鉴定单统计服务
用于管理用户鉴定单的状态统计数据（Redis）
"""
import logging
from typing import Dict, Optional
from app.utils.redis import RedisClient, get_redis
from app.config.settings import ENVIRONMENT

logger = logging.getLogger(__name__)


# 鉴定状态定义
class AppraisalStatus:
    """鉴定状态常量"""
    PENDING = "1"  # 待处理
    IN_REVIEW = "2"  # 审核中
    COMPLETED = "3"  # 已完成
    NEED_SUPPLEMENT = "4"  # 补充材料
    CANCELLED = "5"  # 已取消
    OTHER = "6"  # 其他状态


# 鉴定结果定义
class AppraisalResult:
    """鉴定结果常量"""
    AUTHENTIC = "1"  # 真品
    FAKE = "2"  # 赝品
    NEED_SUPPLEMENT = "3"  # 需补充
    UNCERTAIN = "4"  # 无法判断


class AppraisalStatsService:
    """鉴定单统计服务类"""
    
    # Redis key 过期时间（秒）
    TO_IMPROVE_TTL = 3 * 24 * 60 * 60  # 3天
    COMPLETED_TTL = 7 * 24 * 60 * 60   # 7天
    
    def __init__(self, redis_client: Optional[RedisClient] = None):
        """
        初始化统计服务
        
        Args:
            redis_client: Redis客户端实例，不传则使用默认实例
        """
        self.redis = redis_client or get_redis()
        # Redis key前缀：生产环境用"online"，其他环境用"dev"
        self.env_prefix = "online" if ENVIRONMENT == "production" else "dev"
    
    # ========== Key生成 ==========
    
    def _get_to_improve_key(self, userinfo_id: str) -> str:
        """生成待完善计数的key"""
        return f"{self.env_prefix}:appraisal_to_improve:{userinfo_id}"
    
    def _get_completed_key(self, userinfo_id: str) -> str:
        """生成已完成集合的key"""
        return f"{self.env_prefix}:appraisal_completed:{userinfo_id}"
    
    # ========== 状态判断 ==========
    
    @staticmethod
    def is_to_improve_status(appraisal_status: Optional[str]) -> bool:
        """
        判断是否为待完善状态
        
        待完善状态：补充材料(4)
        """
        if not appraisal_status:
            return False
        return appraisal_status == AppraisalStatus.NEED_SUPPLEMENT
    
    @staticmethod
    def is_completed_status(appraisal_status: Optional[str]) -> bool:
        """
        判断是否为已完成状态
        
        已完成状态：已完成(3)、已取消(5)
        """
        if not appraisal_status:
            return False
        return appraisal_status in [
            AppraisalStatus.COMPLETED,
            AppraisalStatus.CANCELLED
        ]
    
    # ========== 待完善统计 ==========
    
    def increment_to_improve(self, userinfo_id: str, amount: int = 1) -> bool:
        """
        增加待完善计数
        
        Args:
            userinfo_id: 用户ID
            amount: 增加数量，默认1
        
        Returns:
            是否成功
        """
        try:
            key = self._get_to_improve_key(userinfo_id)
            self.redis.incr(key, amount)
            # 设置过期时间（3天）
            self.redis.expire(key, self.TO_IMPROVE_TTL)
            logger.info(f"待完善计数+{amount}: userinfo_id={userinfo_id}, key={key}, TTL={self.TO_IMPROVE_TTL}s")
            return True
        except Exception as e:
            logger.error(f"增加待完善计数失败: {e}", exc_info=True)
            return False
    
    def decrement_to_improve(self, userinfo_id: str, amount: int = 1) -> bool:
        """
        减少待完善计数
        
        Args:
            userinfo_id: 用户ID
            amount: 减少数量，默认1
        
        Returns:
            是否成功
        """
        try:
            key = self._get_to_improve_key(userinfo_id)
            # 确保不会减到负数
            current = self.get_to_improve_count(userinfo_id)
            if current > 0:
                self.redis.decr(key, amount)
                # 刷新过期时间（3天）
                self.redis.expire(key, self.TO_IMPROVE_TTL)
                logger.info(f"待完善计数-{amount}: userinfo_id={userinfo_id}, key={key}, TTL={self.TO_IMPROVE_TTL}s")
            return True
        except Exception as e:
            logger.error(f"减少待完善计数失败: {e}", exc_info=True)
            return False
    
    def get_to_improve_count(self, userinfo_id: str) -> int:
        """
        获取待完善计数
        
        Args:
            userinfo_id: 用户ID
        
        Returns:
            待完善数量
        """
        try:
            key = self._get_to_improve_key(userinfo_id)
            value = self.redis.get(key)
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"获取待完善计数失败: {e}", exc_info=True)
            return 0
    
    def set_to_improve_count(self, userinfo_id: str, count: int) -> bool:
        """
        设置待完善计数（用于初始化或修正）
        
        Args:
            userinfo_id: 用户ID
            count: 数量
        
        Returns:
            是否成功
        """
        try:
            key = self._get_to_improve_key(userinfo_id)
            self.redis.set(key, str(count), ex=self.TO_IMPROVE_TTL)
            logger.info(f"设置待完善计数: userinfo_id={userinfo_id}, count={count}, TTL={self.TO_IMPROVE_TTL}s")
            return True
        except Exception as e:
            logger.error(f"设置待完善计数失败: {e}", exc_info=True)
            return False
    
    # ========== 已完成统计 ==========
    
    def add_to_completed(self, userinfo_id: str, appraisal_id: str) -> bool:
        """
        添加到已完成集合
        
        Args:
            userinfo_id: 用户ID
            appraisal_id: 鉴定单ID
        
        Returns:
            是否成功
        """
        try:
            key = self._get_completed_key(userinfo_id)
            self.redis.sadd(key, appraisal_id)
            # 设置过期时间（7天）
            self.redis.expire(key, self.COMPLETED_TTL)
            logger.info(f"添加到已完成集合: userinfo_id={userinfo_id}, appraisal_id={appraisal_id}, TTL={self.COMPLETED_TTL}s")
            return True
        except Exception as e:
            logger.error(f"添加到已完成集合失败: {e}", exc_info=True)
            return False
    
    def remove_from_completed(self, userinfo_id: str, appraisal_id: str) -> bool:
        """
        从已完成集合移除
        
        Args:
            userinfo_id: 用户ID
            appraisal_id: 鉴定单ID
        
        Returns:
            是否成功
        """
        try:
            key = self._get_completed_key(userinfo_id)
            self.redis.srem(key, appraisal_id)
            # 刷新过期时间（7天）
            self.redis.expire(key, self.COMPLETED_TTL)
            logger.info(f"从已完成集合移除: userinfo_id={userinfo_id}, appraisal_id={appraisal_id}, TTL={self.COMPLETED_TTL}s")
            return True
        except Exception as e:
            logger.error(f"从已完成集合移除失败: {e}", exc_info=True)
            return False
    
    def get_completed_count(self, userinfo_id: str) -> int:
        """
        获取已完成数量
        
        Args:
            userinfo_id: 用户ID
        
        Returns:
            已完成数量
        """
        try:
            key = self._get_completed_key(userinfo_id)
            return self.redis.scard(key)
        except Exception as e:
            logger.error(f"获取已完成数量失败: {e}", exc_info=True)
            return 0
    
    def get_completed_ids(self, userinfo_id: str) -> set:
        """
        获取已完成的鉴定单ID集合
        
        Args:
            userinfo_id: 用户ID
        
        Returns:
            鉴定单ID集合
        """
        try:
            key = self._get_completed_key(userinfo_id)
            return self.redis.smembers(key)
        except Exception as e:
            logger.error(f"获取已完成ID集合失败: {e}", exc_info=True)
            return set()
    
    def is_in_completed(self, userinfo_id: str, appraisal_id: str) -> bool:
        """
        检查鉴定单是否在已完成集合中
        
        Args:
            userinfo_id: 用户ID
            appraisal_id: 鉴定单ID
        
        Returns:
            是否在集合中
        """
        try:
            key = self._get_completed_key(userinfo_id)
            return self.redis.sismember(key, appraisal_id)
        except Exception as e:
            logger.error(f"检查已完成集合失败: {e}", exc_info=True)
            return False
    
    # ========== 综合统计 ==========
    
    def get_user_stats(self, userinfo_id: str) -> Dict[str, int]:
        """
        获取用户的统计数据
        
        Args:
            userinfo_id: 用户ID
        
        Returns:
            统计数据字典
            {
                "to_improve": 待完善数量,
                "completed": 已完成数量
            }
        """
        return {
            "to_improve": self.get_to_improve_count(userinfo_id),
            "completed": self.get_completed_count(userinfo_id)
        }
    
    # ========== 状态变更处理 ==========
    
    def handle_status_change(
        self,
        userinfo_id: str,
        appraisal_id: str,
        old_status: Optional[str],
        new_status: Optional[str]
    ) -> None:
        """
        处理鉴定单状态变更，自动更新统计
        
        业务规则：
        1. 只在状态实际变更时更新统计（old_status不为None）
        2. 已完成(3)是终态，不会再变更
        3. 只根据status判断
        
        Args:
            userinfo_id: 用户ID
            appraisal_id: 鉴定单ID
            old_status: 旧状态
            new_status: 新状态
        """
        try:
            # 规则1: 不在新建时计数，只在状态变更时计数
            if old_status is None:
                logger.info(
                    f"跳过新建鉴定单统计: userinfo_id={userinfo_id}, appraisal_id={appraisal_id}, "
                    f"new_status={new_status}"
                )
                return
            
            # 规则2: 状态没有变化，跳过
            if old_status == new_status:
                logger.debug(
                    f"状态未变化，跳过统计: userinfo_id={userinfo_id}, appraisal_id={appraisal_id}, "
                    f"status={old_status}"
                )
                return
            
            old_is_to_improve = self.is_to_improve_status(old_status)
            new_is_to_improve = self.is_to_improve_status(new_status)
            old_is_completed = self.is_completed_status(old_status)
            new_is_completed = self.is_completed_status(new_status)
            
            # 规则3: 已完成是终态，不应该再变更
            if old_is_completed and not new_is_completed:
                logger.warning(
                    f"检测到从终态变更，跳过: userinfo_id={userinfo_id}, appraisal_id={appraisal_id}, "
                    f"status: {old_status}->{new_status}"
                )
                return
            
            logger.info(
                f"状态变更: userinfo_id={userinfo_id}, appraisal_id={appraisal_id}, "
                f"status: {old_status}->{new_status}, "
                f"old_to_improve={old_is_to_improve}, new_to_improve={new_is_to_improve}, "
                f"old_completed={old_is_completed}, new_completed={new_is_completed}"
            )
            
            # 待完善状态变化
            if not old_is_to_improve and new_is_to_improve:
                # 从非待完善 -> 待完善
                self.increment_to_improve(userinfo_id)
            elif old_is_to_improve and not new_is_to_improve:
                # 从待完善 -> 非待完善
                self.decrement_to_improve(userinfo_id)
            
            # 已完成状态变化（只会从非已完成 -> 已完成）
            if not old_is_completed and new_is_completed:
                # 从非已完成 -> 已完成（终态）
                self.add_to_completed(userinfo_id, appraisal_id)
        
        except Exception as e:
            logger.error(f"处理状态变更失败: {e}", exc_info=True)
    


# 全局统计服务实例
_stats_service: Optional[AppraisalStatsService] = None


def get_appraisal_stats_service() -> AppraisalStatsService:
    """获取统计服务实例（单例模式）"""
    global _stats_service
    if _stats_service is None:
        _stats_service = AppraisalStatsService()
    return _stats_service

