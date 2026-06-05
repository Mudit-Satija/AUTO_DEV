from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Team, User
from app.schemas import TeamCreate, TeamUpdate

def get_team(db: Session, team_id: int) -> Optional[Team]:
    return db.query(Team).filter(Team.id == team_id).first()

def get_teams(db: Session, skip: int = 0, limit: int = 100) -> List[Team]:
    return db.query(Team).offset(skip).limit(limit).all()

def create_team(db: Session, team: TeamCreate, owner_id: int) -> Team:
    db_team = Team(name=team.name, description=team.description, owner_id=owner_id)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

def update_team(db: Session, team_id: int, team_update: TeamUpdate) -> Optional[Team]:
    db_team = get_team(db, team_id)
    if not db_team:
        return None
    for field, value in team_update.dict(exclude_unset=True).items():
        setattr(db_team, field, value)
    db.commit()
    db.refresh(db_team)
    return db_team

def delete_team(db: Session, team_id: int) -> bool:
    db_team = get_team(db, team_id)
    if not db_team:
        return False
    db.delete(db_team)
    db.commit()
    return True

def add_user_to_team(db: Session, team_id: int, user_id: int) -> bool:
    team = get_team(db, team_id)
    user = db.query(User).filter(User.id == user_id).first()
    if not team or not user:
        return False
    if user not in team.members:
        team.members.append(user)
        db.commit()
        return True
    return False

def remove_user_from_team(db: Session, team_id: int, user_id: int) -> bool:
    team = get_team(db, team_id)
    user = db.query(User).filter(User.id == user_id).first()
    if not team or not user:
        return False
    if user in team.members:
        team.members.remove(user)
        db.commit()
        return True
    return False