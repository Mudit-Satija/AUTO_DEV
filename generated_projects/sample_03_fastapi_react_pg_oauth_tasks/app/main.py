from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, users, products
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OAuth Authenticated API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(products.router, prefix="/api/products", tags=["products"])