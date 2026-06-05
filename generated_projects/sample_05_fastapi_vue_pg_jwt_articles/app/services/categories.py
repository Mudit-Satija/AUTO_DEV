from typing import List, Optional
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

def get_categories(db: Session, skip: int = 0, limit: int = 10) -> List[models.Category]:
    return db.query(models.Category).offset(skip).limit(limit).all()

def get_category_by_id(db: Session, category_id: int) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category_id: int, category: schemas.CategoryUpdate) -> Optional[models.Category]:
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        return None
    update_data = category.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int) -> bool:
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        return False
    db.delete(db_category)
    db.commit()
    return True