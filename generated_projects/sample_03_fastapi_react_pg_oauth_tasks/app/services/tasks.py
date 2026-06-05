from sqlalchemy.orm import Session
from app import models, schemas

def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    # Validate project ownership
    project = db.query(models.Project).filter(models.Project.id == task.project_id, models.Project.owner_id == user_id).first()
    if not project:
        raise ValueError("Project not found or not owned by user")
    
    db_task = models.Task(
        title=task.title,
        description=task.description,
        project_id=task.project_id,
        status=task.status,
        priority=task.priority,
        owner_id=user_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100, project_id: int = None):
    query = db.query(models.Task).filter(models.Task.owner_id == user_id)
    if project_id is not None:
        query = query.filter(models.Task.project_id == project_id)
    return query.offset(skip).limit(limit).all()

def get_task(db: Session, task_id: int, user_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == user_id).first()

def update_task(db: Session, task_id: int, task: schemas.TaskUpdate, user_id: int):
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return None
    if task.title is not None:
        db_task.title = task.title
    if task.description is not None:
        db_task.description = task.description
    if task.project_id is not None:
        # Validate new project ownership
        project = db.query(models.Project).filter(models.Project.id == task.project_id, models.Project.owner_id == user_id).first()
        if not project:
            raise ValueError("New project not found or not owned by user")
        db_task.project_id = task.project_id
    if task.status is not None:
        db_task.status = task.status
    if task.priority is not None:
        db_task.priority = task.priority
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int, user_id: int):
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return False
    db.delete(db_task)
    db.commit()
    return True