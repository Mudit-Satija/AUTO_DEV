from app.db.database import db
from app.models.tasks import Task
from app.models.notes import Note
import asyncio

async def seed_data():
    tasks_data = [
        {"title": "Complete project setup", "description": "Initialize FastAPI and React projects", "completed": False},
        {"title": "Write API endpoints", "description": "Implement tasks and notes routes", "completed": False},
        {"title": "Connect frontend to backend", "description": "Fetch tasks and notes from API", "completed": True},
    ]

    notes_data = [
        {"title": "Meeting notes", "content": "Discuss project timeline and deliverables", "tags": ["meeting", "planning"]},
        {"title": "Research findings", "content": "Compare FastAPI vs Flask performance", "tags": ["research", "performance"]},
        {"title": "Deployment checklist", "content": "Dockerize app, configure nginx, set up CI/CD", "tags": ["deployment", "ops"]},
    ]

    await db.tasks.insert_many(tasks_data)
    await db.notes.insert_many(notes_data)

    print("Seed data inserted successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())