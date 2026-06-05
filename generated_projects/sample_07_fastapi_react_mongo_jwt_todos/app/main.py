from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, users, tasks
from app.database import client

app = FastAPI(title="FastAPI React MongoDB JWT App", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])

@app.on_event("shutdown")
def shutdown_db_client():
    client.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI React MongoDB JWT App"}