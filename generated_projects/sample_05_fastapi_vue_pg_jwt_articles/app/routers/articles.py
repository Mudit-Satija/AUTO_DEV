from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, services
from app.database import get_db

router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("/", response_model=List[schemas.Article])
def read_articles(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return services.get_articles(db, skip=skip, limit=limit)

@router.get("/{article_id}", response_model=schemas.Article)
def read_article(article_id: int, db: Session = Depends(get_db)):
    article = services.get_article_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.post("/", response_model=schemas.Article, status_code=status.HTTP_201_CREATED)
def create_article(article: schemas.ArticleCreate, db: Session = Depends(get_db)):
    return services.create_article(db, article)

@router.put("/{article_id}", response_model=schemas.Article)
def update_article(article_id: int, article: schemas.ArticleUpdate, db: Session = Depends(get_db)):
    updated_article = services.update_article(db, article_id, article)
    if not updated_article:
        raise HTTPException(status_code=404, detail="Article not found")
    return updated_article

@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(article_id: int, db: Session = Depends(get_db)):
    success = services.delete_article(db, article_id)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")