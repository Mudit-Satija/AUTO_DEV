from fastapi import FastAPI
from app.routes import router
from app.database import client

app = FastAPI(title="FastAPI React MongoDB JWT App")

app.include_router(router, prefix="/api")

@app.on_event("shutdown")
def shutdown_db_client():
    client.close()