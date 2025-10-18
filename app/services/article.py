from sqlmodel import Session, select, func
from typing import Optional
from datetime import datetime
import time
import uuid

from app.models.article import ArticlePreview
from app.schemas.article import ArticleListData, ArticleDetail, ArticleUpdate, ArticleCreate


class ArticleService:
    
    @staticmethod
    def create_article(article_data: ArticleCreate, current_user, session: Session) -> str:
        """创建新文章"""
        current_time = int(time.time())
        article_id = str(uuid.uuid4()).replace('-', '')
        
        # 创建新文章实例
        new_article = ArticlePreview(
            id=article_id,
            title=article_data.title,
            cover_pic=article_data.cover_pic,
            author=article_data.author,
            rich_content=article_data.rich_content,
            pub_status="1",  # 默认为待发布状态
            create_by=current_user.name,
            update_by=current_user.name,
            created_at=current_time,
            updated_at=current_time,
            is_del="0"
        )
        
        session.add(new_article)
        session.commit()
        session.refresh(new_article)
        
        return new_article.id
    
    @staticmethod
    def get_article_list(
        page: int = 1,
        pageSize: int = 20,
        title: Optional[str] = None,
        author: Optional[str] = None,
        pub_status: Optional[str] = None,
        createStartTime: Optional[str] = None,
        createEndTime: Optional[str] = None,
        session: Session = None
    ) -> ArticleListData:
        
        query = select(ArticlePreview).where(ArticlePreview.is_del != "1")
        
        if title:
            query = query.where(ArticlePreview.title.like(f"%{title}%"))
        
        if author:
            query = query.where(ArticlePreview.author.like(f"%{author}%"))
        
        if pub_status:
            query = query.where(ArticlePreview.pub_status == pub_status)
        
        if createStartTime:
            start_timestamp = int(datetime.fromisoformat(createStartTime.replace('Z', '+00:00')).timestamp())
            query = query.where(ArticlePreview.created_at >= start_timestamp)
        
        if createEndTime:
            end_timestamp = int(datetime.fromisoformat(createEndTime.replace('Z', '+00:00')).timestamp())
            query = query.where(ArticlePreview.created_at <= end_timestamp)
        
        total_query = select(func.count(ArticlePreview.id)).select_from(query.subquery())
        total = session.exec(total_query).one()
        
        offset = (page - 1) * pageSize
        query = query.offset(offset).limit(pageSize)
        
        articles = session.exec(query).all()
        
        article_items = []
        for article in articles:
            article_items.append({
                "id": article.id,
                "author": article.author,
                "cover_pic": article.cover_pic,
                "title": article.title,
                "created_at": article.created_at,
                "create_by": article.create_by,
                "update_by": article.update_by,
                "updated_at": article.updated_at,
                "rich_content": article.rich_content,
                "is_del": article.is_del,
                "pub_status": article.pub_status
            })
        
        return ArticleListData(
            total=total,
            page=page,
            pageSize=pageSize,
            list=article_items
        )
    
    @staticmethod
    def get_article_detail(article_id: str, session: Session) -> Optional[ArticleDetail]:
        article = session.get(ArticlePreview, article_id)
        
        if not article or article.is_del == "1":
            return None
        
        return ArticleDetail(
            id=article.id,
            author=article.author,
            cover_pic=article.cover_pic,
            title=article.title,
            created_at=article.created_at,
            create_by=article.create_by,
            update_by=article.update_by,
            updated_at=article.updated_at,
            rich_content=article.rich_content,
            is_del=article.is_del,
            pub_status=article.pub_status
        )
    
    @staticmethod
    def update_article(article_id: str, article_data: ArticleUpdate, current_user, session: Session) -> bool:
        article = session.get(ArticlePreview, article_id)
        
        if not article or article.is_del == "1":
            return False
        
        update_data = article_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(article, field, value)
        
        article.update_by = current_user.name
        article.updated_at = int(time.time())
        
        session.add(article)
        session.commit()
        session.refresh(article)
        
        return True