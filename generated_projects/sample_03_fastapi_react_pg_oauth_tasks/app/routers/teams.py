from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, services
from app.database import get_db
from app.services.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.TeamOut, status_code=201)
def create_team(
    team: schemas.TeamCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    return services.teams.create_team(db=db, team=team, owner_id=current_user.id)

@router.get("/", response_model=list[schemas.TeamOut])
def read_teams(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    return services.teams.get_teams(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{team_id}", response_model=schemas.TeamOut)
def read_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    db_team = services.teams.get_team(db=db, team_id=team_id, user_id=current_user.id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team

@router.put("/{team_id}", response_model=schemas.TeamOut)
def update_team(
    team_id: int,
    team: schemas.TeamUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    db_team = services.teams.update_team(db=db, team_id=team_id, team=team, user_id=current_user.id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team

@router.delete("/{team_id}", status_code=204)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    success = services.teams.delete_team(db=db, team_id=team_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Team not found")
    return None

@router.post("/{team_id}/members/{user_id}", response_model=schemas.TeamOut)
def add_member_to_team(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    db_team = services.teams.add_member_to_team(db=db, team_id=team_id, user_id=user_id, admin_id=current_user.id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team or user not found")
    return db_team

@router.delete("/{team_id}/members/{user_id}", response_model=schemas.TeamOut)
def remove_member_from_team(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    db_team = services.teams.remove_member_from_team(db=db, team_id=team_id, user_id=user_id, admin_id=current_user.id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team or user not found")
    return db_team