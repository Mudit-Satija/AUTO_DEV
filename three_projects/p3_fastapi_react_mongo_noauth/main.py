from fastapi import FastAPI
from app.db.database import db
from app.routers import tasks, notes

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    await db.connect()

@app.on_event("shutdown")
async def shutdown_db_client():
    await db.disconnect()

app.include_router(tasks.router)
app.include_router(notes.router)