from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, models, services
from app.database import get_db
from app.services.auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/", response_model=schemas.ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return services.reviews.create_review(db=db, review=review, user_id=current_user.id)

@router.get("/", response_model=list[schemas.ReviewOut])
def read_reviews(product_id: int = None, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return services.reviews.get_reviews(db=db, product_id=product_id, skip=skip, limit=limit)

@router.get("/{review_id}", response_model=schemas.ReviewOut)
def read_review(review_id: int, db: Session = Depends(get_db)):
    review = services.reviews.get_review_by_id(db=db, review_id=review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.put("/{review_id}", response_model=schemas.ReviewOut)
def update_review(review_id: int, review: schemas.ReviewUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    updated_review = services.reviews.update_review(db=db, review_id=review_id, review=review, user_id=current_user.id)
    if not updated_review:
        raise HTTPException(status_code=404, detail="Review not found or not authorized")
    return updated_review

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    success = services.reviews.delete_review(db=db, review_id=review_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found or not authorized")
    return None