from fastapi import APIRouter

from app.api.endpoints import auth, user, appraisal, health, appraisal_buy, appraisal_consignment

api_router = APIRouter()

api_router.include_router(health.router, tags=["健康检查"])
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(user.router, prefix="/user", tags=["用户"])
api_router.include_router(appraisal.router, prefix="/appraisal", tags=["鉴定"])
api_router.include_router(appraisal_buy.router, prefix="/appraisal-buy", tags=["鉴宝求购"])
api_router.include_router(appraisal_consignment.router, prefix="/appraisal-consignment", tags=["鉴宝寄卖"])