from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ArticleBase(BaseModel):
    title: str
    content: str
    category_id: int
    tag_ids: Optional[List[int]] = None

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None

class Article(ArticleBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True