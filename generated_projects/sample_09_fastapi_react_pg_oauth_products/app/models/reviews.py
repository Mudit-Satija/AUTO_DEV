from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    comment = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", backref="reviews")