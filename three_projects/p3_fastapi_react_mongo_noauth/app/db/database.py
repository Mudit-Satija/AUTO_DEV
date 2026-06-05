from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGODB_URL)
database = client[settings.DATABASE_NAME]

notes_collection = database["notes"]
tasks_collection = database["tasks"]