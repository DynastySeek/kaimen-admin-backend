from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.services.upload import UploadService
from app.core.dependencies import get_current_user_required
from app.utils.response import success_response
from app.models.user import User

router = APIRouter()


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_required)
):
    upload_service = UploadService()
    result = await upload_service.upload_image(file)
    return success_response(
        data=result,
        message="图片上传成功"
    )


@router.delete("/image")
async def delete_image(
    file_key: str,
    current_user: User = Depends(get_current_user_required)
):
    upload_service = UploadService()
    success = upload_service.delete_image(file_key)
    
    if success:
        return success_response(message="图片删除成功")
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