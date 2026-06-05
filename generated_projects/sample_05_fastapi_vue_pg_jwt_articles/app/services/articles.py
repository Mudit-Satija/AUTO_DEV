from typing import List, Optional
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

def get_articles(db: Session, skip: int = 0, limit: int = 10) -> List[models.Article]:
    return db.query(models.Article).offset(skip).limit(limit).all()

def get_article_by_id(db: Session, article_id: int) -> Optional[models.Article]:
    return db.query(models.Article).filter(models.Article.id == article_id).first()

def create_article(db: Session, article: schemas.ArticleCreate) -> models.Article:
    db_article = models.Article(**article.dict())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def update_article(db: Session, article_id: int, article: schemas.ArticleUpdate) -> Optional[models.Article]:
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not db_article:
        return None
    update_data = article.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_article, key, value)
    db.commit()
    db.refresh(db_article)
    return db_article

def delete_article(db: Session, article_id: int) -> bool:
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not db_article:
        return False
    db.delete(db_article)
    db.commit()
    return True