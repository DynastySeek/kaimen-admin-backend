"""
短信服务封装
提供鉴定结果变更的短信通知功能
"""
import logging
import threading
from typing import Optional, Dict, Any

try:
    from tencentcloud.common import credential
    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
    from tencentcloud.sms.v20210111 import sms_client, models
except ImportError:
    logging.error("腾讯云 SDK 未安装，请运行: pip install tencentcloud-sdk-python")
    raise

from app.config.settings import (
    TENCENT_CLOUD_SECRET_ID,
    TENCENT_CLOUD_SECRET_KEY,
    SMS_SDK_APP_ID,
    SMS_REGION,
    SMS_SIGN_NAME,
    SMS_TEMPLATE_STATUS_COMPLETE,
    SMS_TEMPLATE_DOUBT
)

logger = logging.getLogger(__name__)


class SmsService:
    """短信服务类"""
    
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
        """初始化短信客户端"""
        if not hasattr(self, '_initialized'):
            self._validate_config()
            
            # 实例化认证对象
            cred = credential.Credential(
                TENCENT_CLOUD_SECRET_ID,
                TENCENT_CLOUD_SECRET_KEY
            )
            
            # 实例化短信客户端
            self.client = sms_client.SmsClient(cred, SMS_REGION)
            self._initialized = True
            logger.info("短信服务初始化成功")
    
    @staticmethod
    def _validate_config():
        """验证配置是否完整"""
        required_configs = {
            "TENCENT_CLOUD_SECRET_ID": TENCENT_CLOUD_SECRET_ID,
            "TENCENT_CLOUD_SECRET_KEY": TENCENT_CLOUD_SECRET_KEY,
            "SMS_SDK_APP_ID": SMS_SDK_APP_ID,
            "SMS_SIGN_NAME": SMS_SIGN_NAME,
        }
        
        missing = [key for key, value in required_configs.items() if not value]
        if missing:
            raise ValueError(f"短信配置缺失: {', '.join(missing)}")
    
    @staticmethod
    def _format_phone_number(phone: str) -> str:
        """
        格式化手机号，添加+86前缀
        
        Args:
            phone: 手机号，如 "18811766851"
            
        Returns:
            格式化后的手机号，如 "+8618811766851"
        """
        phone = phone.strip()
        if phone.startswith("+86"):
            return phone
        if phone.startswith("86"):
            return f"+{phone}"
        return f"+86{phone}"
    
    def _send_sms_internal(
        self,
        phone_number: str,
        template_id: str,
        template_params: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        内部发送短信方法
        
        Args:
            phone_number: 手机号（已格式化）
            template_id: 模板ID
            template_params: 模板参数列表
            
        Returns:
            发送结果字典
        """
        try:
            # 构造请求
            req = models.SendSmsRequest()
            req.SmsSdkAppId = SMS_SDK_APP_ID
            req.SignName = SMS_SIGN_NAME
            req.TemplateId = template_id
            req.PhoneNumberSet = [phone_number]
            
            if template_params:
                req.TemplateParamSet = template_params
            
            # 发送短信
            resp = self.client.SendSms(req)
            
            # 解析响应
            result = {
                "success": True,
                "request_id": resp.RequestId,
                "phone_number": phone_number,
                "template_id": template_id
            }
            
            # 检查发送状态
            if resp.SendStatusSet and len(resp.SendStatusSet) > 0:
                status = resp.SendStatusSet[0]
                result["code"] = status.Code
                result["message"] = status.Message
                result["fee"] = status.Fee
                
                if status.Code != "Ok":
                    result["success"] = False
                    logger.warning(
                        f"短信发送失败: phone={phone_number}, "
                        f"code={status.Code}, message={status.Message}"
                    )
            
            return result
            
        except TencentCloudSDKException as e:
            logger.error(
                f"腾讯云SDK异常: code={e.code}, message={e.message}, "
                f"request_id={getattr(e, 'requestId', None)}"
            )
            return {
                "success": False,
                "error_code": e.code,
                "error_message": e.message,
                "phone_number": phone_number,
                "template_id": template_id
            }
        except Exception as e:
            logger.error(f"短信发送异常: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error_code": "UNKNOWN_ERROR",
                "error_message": str(e),
                "phone_number": phone_number,
                "template_id": template_id
            }
    
    def send_appraisal_notification(
        self,
        phone: str,
        appraisal_result: str,
        appraisal_id: str = ""
    ) -> Dict[str, Any]:
        """
        发送鉴定结果通知短信（同步）
        
        Args:
            phone: 用户手机号
            appraisal_result: 鉴定结果 ("1"=真, "2"=假, "3"=存疑, "4"=驳回)
            appraisal_id: 鉴定订单ID（用于日志）
            
        Returns:
            发送结果字典
        """
        # 格式化手机号
        formatted_phone = self._format_phone_number(phone)
        
        # 根据鉴定结果选择模板
        if appraisal_result == "3":
            # 存疑/待完善 - 使用模板 2532458
            template_id = SMS_TEMPLATE_DOUBT
            template_desc = "存疑通知"
        elif appraisal_result in ["1", "2", "4"]:
            # 真/假/驳回 - 使用模板 2532457
            template_id = SMS_TEMPLATE_STATUS_COMPLETE
            template_desc = "状态完成通知"
        else:
            logger.warning(f"未知的鉴定结果类型: {appraisal_result}, 订单ID: {appraisal_id}")
            return {
                "success": False,
                "error_code": "INVALID_RESULT",
                "error_message": f"未知的鉴定结果类型: {appraisal_result}"
            }
        
        logger.info(
            f"准备发送短信: 订单ID={appraisal_id}, 手机号={phone}, "
            f"结果={appraisal_result}, 模板={template_desc}"
        )
        
        # 发送短信（这两个模板都不需要参数）
        result = self._send_sms_internal(
            phone_number=formatted_phone,
            template_id=template_id,
            template_params=None
        )
        
        if result.get("success"):
            logger.info(
                f"短信发送成功: 订单ID={appraisal_id}, 手机号={phone}, "
                f"request_id={result.get('request_id')}"
            )
        else:
            logger.error(
                f"短信发送失败: 订单ID={appraisal_id}, 手机号={phone}, "
                f"错误={result.get('error_message', result.get('message'))}"
            )
        
        return result
    
    def send_appraisal_notification_async(
        self,
        phone: str,
        appraisal_result: str,
        appraisal_id: str = ""
    ) -> None:
        """
        异步发送鉴定结果通知短信
        
        Args:
            phone: 用户手机号
            appraisal_result: 鉴定结果
            appraisal_id: 鉴定订单ID
        """
        # 使用守护线程异步发送，不阻塞主流程
        thread = threading.Thread(
            target=self.send_appraisal_notification,
            args=(phone, appraisal_result, appraisal_id),
            daemon=True,
            name=f"sms-{appraisal_id}"
        )
        thread.start()
        logger.debug(f"启动异步短信发送线程: 订单ID={appraisal_id}")


# 全局单例实例
_sms_service_instance: Optional[SmsService] = None


def get_sms_service() -> Optional[SmsService]:
    """
    获取短信服务实例（延迟初始化）
    
    Returns:
        SmsService实例，如果配置不完整则返回None
    """
    global _sms_service_instance
    
    if _sms_service_instance is None:
        try:
            _sms_service_instance = SmsService()
        except (ValueError, Exception) as e:
            logger.warning(f"短信服务初始化失败，短信功能将不可用: {str(e)}")
            _sms_service_instance = None
    
    return _sms_service_instance

