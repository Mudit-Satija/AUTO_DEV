from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReviewBase(BaseModel):
    rating: int
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    product_id: int

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None

class ReviewOut(ReviewBase):
    id: int
    product_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True