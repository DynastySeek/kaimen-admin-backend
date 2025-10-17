from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Dict

from app.schemas.upload import ImageUploadResponse
from app.services.upload import UploadService
from app.core.dependencies import get_current_user_required
from app.utils.response import success_response
from app.models.user import User

router = APIRouter()


@router.post("/image", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_required)
) -> ImageUploadResponse:
    upload_service = UploadService()
    return await upload_service.upload_image(file)


@router.delete("/image")
async def delete_image(
    file_key: str,
    current_user: User = Depends(get_current_user_required)
) -> Dict[str, str]:
    upload_service = UploadService()
    success = upload_service.delete_image(file_key)
    
    if success:
        return {"message": "图片删除成功"}
    else:
        raise HTTPException(status_code=500, detail="图片删除失败")


@router.get("/buckets", summary="查询存储桶列表")
async def list_buckets(
):
    try:
        upload_service = UploadService()
        buckets = upload_service.list_buckets()
        
        return success_response(
            data=buckets,
            message="查询存储桶列表成功"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"查询失败: {str(e)}"
        )