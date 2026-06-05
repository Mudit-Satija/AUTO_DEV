from sqlalchemy.orm import Session
from app import models, schemas

def create_project(db: Session, project: schemas.ProjectCreate, user_id: int):
    db_project = models.Project(name=project.name, description=project.description, owner_id=user_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_projects(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Project).filter(models.Project.owner_id == user_id).offset(skip).limit(limit).all()

def get_project(db: Session, project_id: int, user_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == user_id).first()

def update_project(db: Session, project_id: int, project: schemas.ProjectUpdate, user_id: int):
    db_project = get_project(db, project_id, user_id)
    if not db_project:
        return None
    if project.name is not None:
        db_project.name = project.name
    if project.description is not None:
        db_project.description = project.description
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int, user_id: int):
    db_project = get_project(db, project_id, user_id)
    if not db_project:
        return False
    db.delete(db_project)
    db.commit()
    return True