from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, services
from app.database import get_db
from app.services.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.TaskOut, status_code=201)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    return services.tasks.create_task(db=db, task=task, user_id=current_user.id)

@router.get("/", response_model=list[schemas.TaskOut])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    project_id: int = None,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    return services.tasks.get_tasks(db=db, user_id=current_user.id, skip=skip, limit=limit, project_id=project_id)

@router.get("/{task_id}", response_model=schemas.TaskOut)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    db_task = services.tasks.get_task(db=db, task_id=task_id, user_id=current_user.id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.put("/{task_id}", response_model=schemas.TaskOut)
def update_task(
    task_id: int,
    task: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    db_task = services.tasks.update_task(db=db, task_id=task_id, task=task, user_id=current_user.id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    success = services.tasks.delete_task(db=db, task_id=task_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return None