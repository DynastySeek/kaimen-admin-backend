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
    WAIT = "1"  # 待鉴定
    IN_REVIEW = "2"  # 审核中
    COMPLETED = "3"  # 已完结
    NEED_SUPPLEMENT = "4"  # 待完善
    CANCELLED = "5"  # 已取消
    OTHER = "6"  # 其他状态


class AppraisalStatsService:
    """鉴定单统计服务类"""
    
    def __init__(self, redis_client: Optional[RedisClient] = None):
        """
        初始化统计服务
        
        Args:
            redis_client: Redis客户端实例，不传则使用默认实例
        """
        self.redis = redis_client or get_redis()
        # Redis key前缀：生产环境用"online"，其他环境用"dev"
        self.env_prefix = "online" if ENVIRONMENT == "production" else "dev"
        # Redis key 过期时间（秒）
        self.completed_ttl = 7 * 24 * 60 * 60  # 7天
    
    # ========== Key生成 ==========
    
    def _get_completed_key(self, userinfo_id: str) -> str:
        """生成已完成集合的key"""
        return f"{self.env_prefix}:appraisal_completed:{userinfo_id}"
    
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
            self.redis.expire(key, self.completed_ttl)
            logger.info(f"添加到已完成集合: userinfo_id={userinfo_id}, appraisal_id={appraisal_id}, TTL={self.completed_ttl}s")
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
            self.redis.expire(key, self.completed_ttl)
            logger.info(f"从已完成集合移除: userinfo_id={userinfo_id}, appraisal_id={appraisal_id}, TTL={self.completed_ttl}s")
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
                "completed": 已完成数量
            }
        """
        return {
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
        1. 只在状态变更为已完成(3)时添加到缓存
        2. 其他状态变更不做任何处理
        
        Args:
            userinfo_id: 用户ID
            appraisal_id: 鉴定单ID
            old_status: 旧状态（可为None）
            new_status: 新状态
        """
        try:
            # 只处理变更为已完成状态的情况
            if new_status == AppraisalStatus.COMPLETED:
                # 检查是否确实是状态变更（不是已经完成的）
                if old_status != new_status:
                    logger.info(
                        f"状态变更为已完成: userinfo_id={userinfo_id}, "
                        f"appraisal_id={appraisal_id}, status: {old_status}->{new_status}"
                    )
                    self.add_to_completed(userinfo_id, appraisal_id)
                else:
                    logger.debug(
                        f"状态未变化（已是已完成），跳过: userinfo_id={userinfo_id}, "
                        f"appraisal_id={appraisal_id}"
                    )
            else:
                logger.debug(
                    f"状态未变更为已完成，跳过统计: userinfo_id={userinfo_id}, "
                    f"appraisal_id={appraisal_id}, status: {old_status}->{new_status}"
                )
        
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
