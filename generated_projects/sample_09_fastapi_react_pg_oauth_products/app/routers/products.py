from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, models, services
from app.database import get_db

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return services.products.create_product(db=db, product=product)

@router.get("/", response_model=list[schemas.ProductOut])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return services.products.get_products(db=db, skip=skip, limit=limit)

@router.get("/{product_id}", response_model=schemas.ProductOut)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = services.products.get_product_by_id(db=db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    updated_product = services.products.update_product(db=db, product_id=product_id, product=product)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    success = services.products.delete_product(db=db, product_id=product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return None