from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, services
from app.database import get_db
from app.services.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.ProjectOut, status_code=201)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    return services.projects.create_project(db=db, project=project, user_id=current_user.id)

@router.get("/", response_model=list[schemas.ProjectOut])
def read_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    return services.projects.get_projects(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{project_id}", response_model=schemas.ProjectOut)
def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    db_project = services.projects.get_project(db=db, project_id=project_id, user_id=current_user.id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.put("/{project_id}", response_model=schemas.ProjectOut)
def update_project(
    project_id: int,
    project: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    db_project = services.projects.update_project(db=db, project_id=project_id, project=project, user_id=current_user.id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    success = services.projects.delete_project(db=db, project_id=project_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return None