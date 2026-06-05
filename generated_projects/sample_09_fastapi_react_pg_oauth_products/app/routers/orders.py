from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, database, oauth2

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

@router.get("/", response_model=List[schemas.Order])
def get_orders(db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    orders = db.query(models.Order).filter(models.Order.user_id == current_user.id).all()
    return orders

@router.get("/{id}", response_model=schemas.Order)
def get_order(id: int, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == id, models.Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order

@router.post("/", response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
def create_order(order: schemas.OrderCreate, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    new_order = models.Order(user_id=current_user.id, **order.dict())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.put("/{id}", response_model=schemas.Order)
def update_order(id: int, order: schemas.OrderUpdate, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    order_query = db.query(models.Order).filter(models.Order.id == id, models.Order.user_id == current_user.id)
    existing_order = order_query.first()
    if not existing_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    order_query.update(order.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    return order_query.first()

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(id: int, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    order_query = db.query(models.Order).filter(models.Order.id == id, models.Order.user_id == current_user.id)
    if not order_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    order_query.delete(synchronize_session=False)
    db.commit()
    return None