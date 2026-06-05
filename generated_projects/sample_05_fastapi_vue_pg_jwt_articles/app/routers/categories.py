from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, services
from app.database import get_db

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[schemas.Category])
def read_categories(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return services.get_categories(db, skip=skip, limit=limit)

@router.get("/{category_id}", response_model=schemas.Category)
def read_category(category_id: int, db: Session = Depends(get_db)):
    category = services.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return services.create_category(db, category)

@router.put("/{category_id}", response_model=schemas.Category)
def update_category(category_id: int, category: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    updated_category = services.update_category(db, category_id, category)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    success = services.delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")