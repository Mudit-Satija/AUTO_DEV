from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="FastAPI React MongoDB JWT App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(os.getenv("MONGODB_URI"))
    app.database = app.mongodb_client[os.getenv("MONGODB_NAME")]

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()