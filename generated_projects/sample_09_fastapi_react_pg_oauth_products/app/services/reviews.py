from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Review, User, Product
from app.schemas import ReviewCreate, ReviewUpdate, ReviewResponse


def get_reviews_by_product(db: Session, product_id: int) -> List[ReviewResponse]:
    return db.query(Review).filter(Review.product_id == product_id).all()


def get_review_by_id(db: Session, review_id: int) -> Optional[Review]:
    return db.query(Review).filter(Review.id == review_id).first()


def create_review(db: Session, review_data: ReviewCreate, user_id: int) -> Review:
    product = db.query(Product).filter(Product.id == review_data.product_id).first()
    if not product:
        raise ValueError("Product not found")

    db_review = Review(
        product_id=review_data.product_id,
        user_id=user_id,
        rating=review_data.rating,
        comment=review_data.comment,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def update_review(db: Session, review_id: int, review_data: ReviewUpdate, user_id: int) -> Optional[Review]:
    db_review = db.query(Review).filter(Review.id == review_id, Review.user_id == user_id).first()
    if not db_review:
        return None

    if review_data.rating is not None:
        db_review.rating = review_data.rating
    if review_data.comment is not None:
        db_review.comment = review_data.comment
    db_review.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_review)
    return db_review


def delete_review(db: Session, review_id: int, user_id: int) -> bool:
    db_review = db.query(Review).filter(Review.id == review_id, Review.user_id == user_id).first()
    if not db_review:
        return False

    db.delete(db_review)
    db.commit()
    return True