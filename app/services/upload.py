import os
import uuid
from datetime import datetime
from typing import Optional
from fastapi import UploadFile, HTTPException
from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosServiceError, CosClientError

from app.schemas.upload import ImageUploadResponse, UploadConfig
from app.config.settings import COS_SECRET_ID, COS_SECRET_KEY, COS_REGION, COS_BUCKET


class UploadService:
    
    def __init__(self):
        self.cos_client = self._get_cos_client()
        self.bucket = COS_BUCKET
        self.region = COS_REGION
        self.config = UploadConfig()
        
        if not self.cos_client or not self.bucket:
            raise ValueError("腾讯云COS配置不完整，请检查环境变量")
    
    def _get_cos_client(self):
        config = CosConfig(
            Region=COS_REGION,
            SecretId=COS_SECRET_ID,
            SecretKey=COS_SECRET_KEY,
            Scheme='https'
        )
        
        client = CosS3Client(config)
        return client
    
    @staticmethod
    def validate_image_file(file: UploadFile, config: UploadConfig = None) -> bool:
        if config is None:
            config = UploadConfig()
        
        if file.size > config.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制，最大允许 {config.max_file_size / 1024 / 1024:.1f}MB"
            )
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in config.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式，仅支持: {', '.join(config.allowed_extensions)}"
            )
        
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="文件类型错误，仅支持图片文件"
            )
        
        return True
    
    def generate_file_key(self, filename: str, folder: str = "images") -> str:
        file_ext = os.path.splitext(filename)[1].lower()
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4()).replace('-', '')
        file_key = f"{folder}/{timestamp}/{unique_id}{file_ext}"
        return file_key
    
    async def upload_image(self, file: UploadFile, folder: str = "images") -> ImageUploadResponse:
        try:
            self.validate_image_file(file)
            file_key = self.generate_file_key(file.filename, folder)
            file_content = await file.read()
            
            response = self.cos_client.put_object(
                Bucket=self.bucket,
                Body=file_content,
                Key=file_key,
                ContentType=file.content_type
            )
            
            file_url = f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{file_key}"
            
            return ImageUploadResponse(
                url=file_url,
                key=file_key,
                size=file.size,
                content_type=file.content_type
            )
            
        except CosServiceError as e:
            raise HTTPException(
                status_code=500,
                detail=f"COS服务错误: {e.get_error_msg()}"
            )
        except CosClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"COS客户端错误: {e.get_error_msg()}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"上传失败: {str(e)}"
            )
    
    def delete_image(self, file_key: str) -> bool:
        try:
            self.cos_client.delete_object(
                Bucket=self.bucket,
                Key=file_key
            )
            return True
        except Exception as e:
            print(f"删除文件失败: {str(e)}")
            return False
    
    def list_buckets(self):
        try:
            response = self.cos_client.list_buckets()
            return response
        except (CosServiceError, CosClientError) as e:
            raise HTTPException(
                status_code=500,
                detail=f"查询存储桶失败: {e.get_error_msg()}"
            )