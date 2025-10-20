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
    COMPLETED = "3"  # 已完结（终态）
    NEED_SUPPLEMENT = "4"  # 待完善
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
    
    def _get_wait_key(self, userinfo_id: str) -> str:
        """生成待鉴定计数的key"""
        return f"{self.env_prefix}:appraisal_wait:{userinfo_id}"
    
    def _get_to_improve_key(self, userinfo_id: str) -> str:
        """生成待完善计数的key"""
        return f"{self.env_prefix}:appraisal_to_improve:{userinfo_id}"
    
    def _get_completed_key(self, userinfo_id: str) -> str:
        """生成已完成集合的key"""
        return f"{self.env_prefix}:appraisal_completed:{userinfo_id}"
    
    # ========== 状态判断 ==========
    
    @staticmethod
    def is_cached_status(status: Optional[str]) -> bool:
        """判断是否为需要缓存的状态"""
        if not status:
            return False
        return status in [
            AppraisalStatus.WAIT,           # "1" 待鉴定
            AppraisalStatus.COMPLETED,       # "3" 已完结
            AppraisalStatus.NEED_SUPPLEMENT  # "4" 待完善
        ]
    
    @staticmethod
    def is_final_status(status: Optional[str]) -> bool:
        """判断是否为终态（不允许转换）"""
        if not status:
            return False
        return status == AppraisalStatus.COMPLETED  # "3" 已完结
    
    # ========== 待鉴定统计 ==========
    
    def increment_wait(self, userinfo_id: str, amount: int = 1) -> bool:
        """
        增加待鉴定计数
        
        Args:
            userinfo_id: 用户ID
            amount: 增加数量，默认1
        
        Returns:
            是否成功
        """
        try:
            key = self._get_wait_key(userinfo_id)
            self.redis.incr(key, amount)
            # 设置过期时间（3天）
            self.redis.expire(key, self.TO_IMPROVE_TTL)
            logger.info(f"待鉴定计数+{amount}: userinfo_id={userinfo_id}, key={key}, TTL={self.TO_IMPROVE_TTL}s")
            return True
        except Exception as e:
            logger.error(f"增加待鉴定计数失败: {e}", exc_info=True)
            return False
    
    def decrement_wait(self, userinfo_id: str, amount: int = 1) -> bool:
        """
        减少待鉴定计数（使用Lua脚本防止负数）
        
        Args:
            userinfo_id: 用户ID
            amount: 减少数量，默认1
        
        Returns:
            是否成功
        """
        try:
            key = self._get_wait_key(userinfo_id)
            # 使用Lua脚本保证原子性并防止负数，同时设置TTL
            lua_script = """
            local current = tonumber(redis.call('GET', KEYS[1]) or '0')
            if current > 0 then
                local result = redis.call('DECRBY', KEYS[1], ARGV[1])
                redis.call('EXPIRE', KEYS[1], ARGV[2])
                return result
            else
                return 0
            end
            """
            client = self.redis.get_client()
            client.eval(lua_script, 1, key, amount, self.TO_IMPROVE_TTL)
            logger.info(f"待鉴定计数-{amount}: userinfo_id={userinfo_id}, key={key}, TTL={self.TO_IMPROVE_TTL}s")
            return True
        except Exception as e:
            logger.error(f"减少待鉴定计数失败: {e}", exc_info=True)
            return False
    
    def get_wait_count(self, userinfo_id: str) -> int:
        """
        获取待鉴定计数
        
        Args:
            userinfo_id: 用户ID
        
        Returns:
            待鉴定数量
        """
        try:
            key = self._get_wait_key(userinfo_id)
            value = self.redis.get(key)
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"获取待鉴定计数失败: {e}", exc_info=True)
            return 0
    
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
        减少待完善计数（使用Lua脚本防止负数）
        
        Args:
            userinfo_id: 用户ID
            amount: 减少数量，默认1
        
        Returns:
            是否成功
        """
        try:
            key = self._get_to_improve_key(userinfo_id)
            # 使用Lua脚本保证原子性并防止负数，同时设置TTL
            lua_script = """
            local current = tonumber(redis.call('GET', KEYS[1]) or '0')
            if current > 0 then
                local result = redis.call('DECRBY', KEYS[1], ARGV[1])
                redis.call('EXPIRE', KEYS[1], ARGV[2])
                return result
            else
                return 0
            end
            """
            client = self.redis.get_client()
            client.eval(lua_script, 1, key, amount, self.TO_IMPROVE_TTL)
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
                "wait": 待鉴定数量,
                "to_improve": 待完善数量,
                "completed": 已完成数量
            }
        """
        return {
            "wait": self.get_wait_count(userinfo_id),
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
        2. 已完结(3)是终态，不允许转换
        3. 管理三种状态：待鉴定(1)、已完结(3)、待完善(4)
        4. A->B转换：如果A在三种状态内则A-1，如果B在三种状态内则B+1
        
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
                    f"跳过新建鉴定单统计: userinfo_id={userinfo_id}, "
                    f"appraisal_id={appraisal_id}, new_status={new_status}"
                )
                return
            
            # 规则2: 状态没有变化，跳过
            if old_status == new_status:
                logger.debug(
                    f"状态未变化，跳过统计: userinfo_id={userinfo_id}, "
                    f"appraisal_id={appraisal_id}, status={old_status}"
                )
                return
            
            # 规则3: 已完结是终态，不允许转换
            if self.is_final_status(old_status):
                logger.warning(
                    f"检测到从终态变更，跳过: userinfo_id={userinfo_id}, "
                    f"appraisal_id={appraisal_id}, status: {old_status}->{new_status}"
                )
                return
            
            old_is_cached = self.is_cached_status(old_status)
            new_is_cached = self.is_cached_status(new_status)
            
            logger.info(
                f"状态变更: userinfo_id={userinfo_id}, appraisal_id={appraisal_id}, "
                f"status: {old_status}->{new_status}, "
                f"old_is_cached={old_is_cached}, new_is_cached={new_is_cached}"
            )
            # 步骤1: 如果旧状态在三种状态内，需要减少对应计数
            if old_is_cached:
                if old_status == AppraisalStatus.WAIT:
                    self.decrement_wait(userinfo_id)
                elif old_status == AppraisalStatus.NEED_SUPPLEMENT:
                    self.decrement_to_improve(userinfo_id)
                elif old_status == AppraisalStatus.COMPLETED:
                    # 已完结状态移除（虽然终态不应该转换，但为了完整性）
                    self.remove_from_completed(userinfo_id, appraisal_id)

            # 步骤2: 如果新状态在三种状态内，需要增加对应计数
            if new_is_cached:
                if new_status == AppraisalStatus.WAIT:
                    self.increment_wait(userinfo_id)
                elif new_status == AppraisalStatus.NEED_SUPPLEMENT:
                    self.increment_to_improve(userinfo_id)
                elif new_status == AppraisalStatus.COMPLETED:
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

