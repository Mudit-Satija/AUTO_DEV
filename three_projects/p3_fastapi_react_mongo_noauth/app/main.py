from fastapi import FastAPI
from app.core.config import settings
from app.db.database import db
from app.routers.tasks import router as tasks_router
from app.routers.notes import router as notes_router

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

@app.on_event("startup")
async def startup_db_client():
    db.client = db.get_client()

@app.on_event("shutdown")
async def shutdown_db_client():
    db.client.close()

app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(notes_router, prefix="/api/v1/notes", tags=["notes"])