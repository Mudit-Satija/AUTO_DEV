from sqlalchemy.orm import Session
from app import models, schemas

def create_order(db: Session, order: schemas.OrderCreate, user_id: int):
    db_order = models.Order(**order.dict(), user_id=user_id, status="pending")
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders_by_user(db: Session, user_id: int):
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()

def get_order_by_id(db: Session, order_id: int, user_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id, models.Order.user_id == user_id).first()