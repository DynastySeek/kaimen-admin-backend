"""
Redis 连接和操作工具
"""
import redis
from typing import Optional, Any, Union
from app.config.settings import REDIS_HOST, REDIS_PORT, REDIS_USER, REDIS_PASSWORD, REDIS_DB


class RedisClient:
    """Redis 客户端封装类"""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
    
    def get_client(self) -> redis.Redis:
        """获取 Redis 客户端连接"""
        if self._client is None:
            self._client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                username=REDIS_USER,
                password=REDIS_PASSWORD,
                db=REDIS_DB,
                decode_responses=True,  # 自动解码响应为字符串
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
        return self._client
    
    def ping(self) -> bool:
        """检查 Redis 连接状态"""
        try:
            client = self.get_client()
            return client.ping()
        except Exception:
            return False
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """设置键值对"""
        try:
            client = self.get_client()
            return client.set(key, value, ex=ex)
        except Exception:
            return False
    
    def get(self, key: str) -> Optional[str]:
        """获取键值"""
        try:
            client = self.get_client()
            return client.get(key)
        except Exception:
            return None
    
    def delete(self, key: str) -> bool:
        """删除键"""
        try:
            client = self.get_client()
            return bool(client.delete(key))
        except Exception:
            return False
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            client = self.get_client()
            return bool(client.exists(key))
        except Exception:
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """设置键过期时间"""
        try:
            client = self.get_client()
            return client.expire(key, seconds)
        except Exception:
            return False
    
    def ttl(self, key: str) -> int:
        """获取键的剩余过期时间"""
        try:
            client = self.get_client()
            return client.ttl(key)
        except Exception:
            return -1
    
    def hset(self, name: str, mapping: dict) -> int:
        """设置哈希字段"""
        try:
            client = self.get_client()
            return client.hset(name, mapping=mapping)
        except Exception:
            return 0
    
    def hget(self, name: str, key: str) -> Optional[str]:
        """获取哈希字段值"""
        try:
            client = self.get_client()
            return client.hget(name, key)
        except Exception:
            return None
    
    def hgetall(self, name: str) -> dict:
        """获取所有哈希字段"""
        try:
            client = self.get_client()
            return client.hgetall(name)
        except Exception:
            return {}
    
    def hdel(self, name: str, *keys: str) -> int:
        """删除哈希字段"""
        try:
            client = self.get_client()
            return client.hdel(name, *keys)
        except Exception:
            return 0
    
    def lpush(self, name: str, *values: Any) -> int:
        """从左侧推入列表"""
        try:
            client = self.get_client()
            return client.lpush(name, *values)
        except Exception:
            return 0
    
    def rpop(self, name: str) -> Optional[str]:
        """从右侧弹出列表元素"""
        try:
            client = self.get_client()
            return client.rpop(name)
        except Exception:
            return None
    
    def llen(self, name: str) -> int:
        """获取列表长度"""
        try:
            client = self.get_client()
            return client.llen(name)
        except Exception:
            return 0
    
    # ========== Set 操作 ==========
    
    def sadd(self, name: str, *values: Any) -> int:
        """添加元素到集合"""
        try:
            client = self.get_client()
            return client.sadd(name, *values)
        except Exception:
            return 0
    
    def srem(self, name: str, *values: Any) -> int:
        """从集合中删除元素"""
        try:
            client = self.get_client()
            return client.srem(name, *values)
        except Exception:
            return 0
    
    def smembers(self, name: str) -> set:
        """获取集合所有成员"""
        try:
            client = self.get_client()
            return client.smembers(name)
        except Exception:
            return set()
    
    def scard(self, name: str) -> int:
        """获取集合元素数量"""
        try:
            client = self.get_client()
            return client.scard(name)
        except Exception:
            return 0
    
    def sismember(self, name: str, value: Any) -> bool:
        """检查元素是否在集合中"""
        try:
            client = self.get_client()
            return client.sismember(name, value)
        except Exception:
            return False
    
    # ========== 计数操作 ==========
    
    def incr(self, name: str, amount: int = 1) -> int:
        """递增计数器"""
        try:
            client = self.get_client()
            return client.incr(name, amount)
        except Exception:
            return 0
    
    def decr(self, name: str, amount: int = 1) -> int:
        """递减计数器"""
        try:
            client = self.get_client()
            return client.decr(name, amount)
        except Exception:
            return 0
    
    def incrby(self, name: str, amount: int) -> int:
        """按指定值递增"""
        try:
            client = self.get_client()
            return client.incrby(name, amount)
        except Exception:
            return 0
    
    def decrby(self, name: str, amount: int) -> int:
        """按指定值递减"""
        try:
            client = self.get_client()
            return client.decrby(name, amount)
        except Exception:
            return 0
    
    def close(self):
        """关闭连接"""
        if self._client:
            self._client.close()
            self._client = None


# 全局 Redis 客户端实例
redis_client = RedisClient()


def get_redis() -> RedisClient:
    """获取 Redis 客户端依赖注入"""
    return redis_client
