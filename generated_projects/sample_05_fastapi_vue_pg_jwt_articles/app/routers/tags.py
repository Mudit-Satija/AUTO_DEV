from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, services
from app.database import get_db

router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("/", response_model=List[schemas.Tag])
def read_tags(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return services.get_tags(db, skip=skip, limit=limit)

@router.get("/{tag_id}", response_model=schemas.Tag)
def read_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = services.get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

@router.post("/", response_model=schemas.Tag, status_code=status.HTTP_201_CREATED)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    return services.create_tag(db, tag)

@router.put("/{tag_id}", response_model=schemas.Tag)
def update_tag(tag_id: int, tag: schemas.TagUpdate, db: Session = Depends(get_db)):
    updated_tag = services.update_tag(db, tag_id, tag)
    if not updated_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return updated_tag

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    success = services.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")