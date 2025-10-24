"""
短信延迟发送管理器
提供鉴定状态变更的延迟短信通知功能
"""
import logging
import threading
import time
from typing import Dict, Optional, Any
from threading import Timer

from app.config.settings import SMS_DELAY_SECONDS
from app.services.sms import get_sms_service

logger = logging.getLogger(__name__)


class SmsDelayManager:
    """短信延迟发送管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化延迟发送管理器"""
        if not hasattr(self, '_initialized'):
            self._pending_tasks: Dict[str, Dict[str, Any]] = {}
            self._task_lock = threading.Lock()
            self._initialized = True
            logger.info(f"短信延迟发送管理器初始化成功，延迟时间: {SMS_DELAY_SECONDS}秒")
    
    def schedule_delayed_sms(
        self, 
        appraisal_id: str, 
        phone: str, 
        status: str
    ) -> bool:
        """
        调度延迟短信发送
        
        Args:
            appraisal_id: 鉴定订单ID
            phone: 用户手机号
            status: 鉴定状态
            
        Returns:
            bool: 是否成功调度
        """
        try:
            with self._task_lock:
                # 如果该订单已有待发送任务，先取消旧任务
                if appraisal_id in self._pending_tasks:
                    self._cancel_existing_task(appraisal_id)
                
                # 创建新的延迟任务
                timer = Timer(
                    SMS_DELAY_SECONDS,
                    self._execute_send,
                    args=(appraisal_id,)
                )
                timer.daemon = False  # 确保应用关闭前完成发送
                
                # 记录任务信息
                task_info = {
                    "timer": timer,
                    "phone": phone,
                    "status": status,
                    "scheduled_time": time.time() + SMS_DELAY_SECONDS,
                    "created_time": time.time()
                }
                
                self._pending_tasks[appraisal_id] = task_info
                timer.start()
                
                logger.info(
                    f"已调度延迟短信发送: 订单ID={appraisal_id}, 手机号={phone}, "
                    f"状态={status}, 延迟={SMS_DELAY_SECONDS}秒"
                )
                
                return True
                
        except Exception as e:
            logger.error(
                f"调度延迟短信发送失败: 订单ID={appraisal_id}, 错误={str(e)}",
                exc_info=True
            )
            return False
    
    def cancel_delayed_sms(self, appraisal_id: str) -> bool:
        """
        取消指定订单的延迟任务
        
        Args:
            appraisal_id: 鉴定订单ID
            
        Returns:
            bool: 是否成功取消
        """
        try:
            with self._task_lock:
                if appraisal_id in self._pending_tasks:
                    self._cancel_existing_task(appraisal_id)
                    logger.info(f"已取消延迟短信发送: 订单ID={appraisal_id}")
                    return True
                else:
                    logger.debug(f"未找到待取消的延迟任务: 订单ID={appraisal_id}")
                    return False
                    
        except Exception as e:
            logger.error(
                f"取消延迟短信发送失败: 订单ID={appraisal_id}, 错误={str(e)}",
                exc_info=True
            )
            return False
    
    def _cancel_existing_task(self, appraisal_id: str) -> None:
        """取消已存在的任务"""
        if appraisal_id in self._pending_tasks:
            task_info = self._pending_tasks[appraisal_id]
            timer = task_info.get("timer")
            if timer and timer.is_alive():
                timer.cancel()
                logger.debug(f"已取消旧延迟任务: 订单ID={appraisal_id}")
            del self._pending_tasks[appraisal_id]
    
    def _execute_send(self, appraisal_id: str) -> None:
        """
        Timer 到期后执行的回调函数
        
        Args:
            appraisal_id: 鉴定订单ID
        """
        try:
            with self._task_lock:
                if appraisal_id not in self._pending_tasks:
                    logger.warning(f"延迟任务已不存在: 订单ID={appraisal_id}")
                    return
                
                task_info = self._pending_tasks[appraisal_id]
                phone = task_info.get("phone")
                status = task_info.get("status")
                
                # 从内存中移除任务记录
                del self._pending_tasks[appraisal_id]
            
            # 获取短信服务并发送
            sms_service = get_sms_service()
            if sms_service:
                result = sms_service.send_status_notification(
                    phone=phone,
                    appraisal_status=status,
                    appraisal_id=appraisal_id
                )
                
                if result.get("success"):
                    logger.info(
                        f"延迟短信发送成功: 订单ID={appraisal_id}, 手机号={phone}, "
                        f"状态={status}"
                    )
                else:
                    logger.error(
                        f"延迟短信发送失败: 订单ID={appraisal_id}, 手机号={phone}, "
                        f"状态={status}, 错误={result.get('error_message', result.get('message'))}"
                    )
            else:
                logger.error(f"短信服务不可用，延迟短信发送失败: 订单ID={appraisal_id}")
                
        except Exception as e:
            logger.error(
                f"执行延迟短信发送异常: 订单ID={appraisal_id}, 错误={str(e)}",
                exc_info=True
            )
    
    def get_pending_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有待发送任务（用于调试/监控）
        
        Returns:
            Dict: 待发送任务字典
        """
        with self._task_lock:
            # 返回任务信息的副本，不包含 Timer 对象
            result = {}
            for appraisal_id, task_info in self._pending_tasks.items():
                result[appraisal_id] = {
                    "phone": task_info.get("phone"),
                    "status": task_info.get("status"),
                    "scheduled_time": task_info.get("scheduled_time"),
                    "created_time": task_info.get("created_time"),
                    "remaining_seconds": max(0, int(task_info.get("scheduled_time", 0) - time.time()))
                }
            return result
    
    def get_task_count(self) -> int:
        """获取待发送任务数量"""
        with self._task_lock:
            return len(self._pending_tasks)
    
    def cancel_all_tasks(self) -> int:
        """
        取消所有待发送任务（用于应用关闭时）
        
        Returns:
            int: 取消的任务数量
        """
        with self._task_lock:
            count = len(self._pending_tasks)
            for appraisal_id in list(self._pending_tasks.keys()):
                self._cancel_existing_task(appraisal_id)
            logger.info(f"已取消所有延迟短信任务，共 {count} 个")
            return count


# 全局单例实例
_sms_delay_manager_instance: Optional[SmsDelayManager] = None


def get_sms_delay_manager() -> Optional[SmsDelayManager]:
    """
    获取短信延迟发送管理器实例（延迟初始化）
    
    Returns:
        SmsDelayManager实例，如果初始化失败则返回None
    """
    global _sms_delay_manager_instance
    
    if _sms_delay_manager_instance is None:
        try:
            _sms_delay_manager_instance = SmsDelayManager()
        except Exception as e:
            logger.warning(f"短信延迟发送管理器初始化失败，延迟发送功能将不可用: {str(e)}")
            _sms_delay_manager_instance = None
    
    return _sms_delay_manager_instance
