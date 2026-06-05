from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Tag
from app.schemas import TagCreate, TagUpdate

def get_tags(db: Session, skip: int = 0, limit: int = 100) -> List[Tag]:
    return db.query(Tag).offset(skip).limit(limit).all()

def get_tag_by_id(db: Session, tag_id: int) -> Optional[Tag]:
    return db.query(Tag).filter(Tag.id == tag_id).first()

def create_tag(db: Session, tag: TagCreate) -> Tag:
    db_tag = Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def update_tag(db: Session, tag_id: int, tag_update: TagUpdate) -> Optional[Tag]:
    db_tag = get_tag_by_id(db, tag_id)
    if not db_tag:
        return None
    if tag_update.name is not None:
        db_tag.name = tag_update.name
    db.commit()
    db.refresh(db_tag)
    return db_tag

def delete_tag(db: Session, tag_id: int) -> bool:
    db_tag = get_tag_by_id(db, tag_id)
    if not db_tag:
        return False
    db.delete(db_tag)
    db.commit()
    return True