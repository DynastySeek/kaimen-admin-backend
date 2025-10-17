from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session
from typing import Optional

from app.services.article import ArticleService
from app.schemas.article import ArticleListData, ArticleDetail, ArticleUpdate, ArticleCreate
from app.utils.db import get_session
from app.utils.response import success_response
from app.core.dependencies import get_current_user_required
from app.models.user import User

router = APIRouter()


@router.post("/create", summary="创建文章")
def create_article(
    article_data: ArticleCreate,
    current_user: User = Depends(get_current_user_required),
    session: Session = Depends(get_session)
):
    """创建新文章"""
    try:
        article_id = ArticleService.create_article(
            article_data=article_data,
            current_user=current_user,
            session=session
        )
        return success_response(
            data={"id": article_id},
            message="文章创建成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建文章失败: {str(e)}"
        )


@router.get("/list")
def get_article_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    pub_status: Optional[str] = Query(None),
    createStartTime: Optional[str] = Query(None),
    createEndTime: Optional[str] = Query(None),
    session: Session = Depends(get_session)
):
    try:
        data = ArticleService.get_article_list(
            page=page,
            pageSize=pageSize,
            title=title,
            author=author,
            pub_status=pub_status,
            createStartTime=createStartTime,
            createEndTime=createEndTime,
            session=session
        )
        
        return success_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/detail")
def get_article_detail(
    id: str = Query(...),
    session: Session = Depends(get_session)
):
    try:
        data = ArticleService.get_article_detail(id, session)
        
        if not data:
            raise HTTPException(status_code=404, detail="文章不存在")
        
        return success_response(data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.put("/update", summary="更新文章")
def update_article(
    article_id: int = Query(..., description="文章ID"),
    article_data: ArticleUpdate = ...,
    current_user: User = Depends(get_current_user_required),
    session: Session = Depends(get_session)
):
    """更新文章"""
    try:
        result = ArticleService.update_article(
            article_id=article_id,
            article_data=article_data,
            current_user=current_user,
            session=session
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新文章失败: {str(e)}"
        )


@router.put("/enable", summary="启用文章")
def enable_article(
    article_id: int = Query(..., description="文章ID"),
    current_user: User = Depends(get_current_user_required),
    session: Session = Depends(get_session)
):
    """启用文章（设为已发布状态）"""
    try:
        article_data = ArticleUpdate(pub_status="2")  # 2-已发布
        result = ArticleService.update_article(
            article_id=article_id,
            article_data=article_data,
            current_user=current_user,
            session=session
        )
        return success_response(
            data={"id": article_id, "pub_status": "2"},
            message="文章启用成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启用文章失败: {str(e)}"
        )


@router.put("/disable", summary="禁用文章")
def disable_article(
    article_id: int = Query(..., description="文章ID"),
    current_user: User = Depends(get_current_user_required),
    session: Session = Depends(get_session)
):
    """禁用文章（设为已下线状态）"""
    try:
        article_data = ArticleUpdate(pub_status="3")  # 3-已下线
        result = ArticleService.update_article(
            article_id=article_id,
            article_data=article_data,
            current_user=current_user,
            session=session
        )
        return success_response(
            data={"id": article_id, "pub_status": "3"},
            message="文章禁用成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"禁用文章失败: {str(e)}"
        )