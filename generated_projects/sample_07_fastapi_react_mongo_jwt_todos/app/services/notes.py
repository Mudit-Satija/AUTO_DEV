from app.database import get_database
from bson import ObjectId
from datetime import datetime

db = get_database()

async def create_note(note_data: dict):
    note_data["created_at"] = datetime.utcnow()
    note_data["updated_at"] = datetime.utcnow()
    result = await db.notes.insert_one(note_data)
    note_data["_id"] = str(result.inserted_id)
    return note_data

async def get_notes(owner: str):
    notes = []
    async for note in db.notes.find({"owner": owner}):
        note["_id"] = str(note["_id"])
        notes.append(note)
    return notes

async def get_note_by_id(note_id: str):
    note = await db.notes.find_one({"_id": ObjectId(note_id)})
    if note:
        note["_id"] = str(note["_id"])
    return note

async def update_note(note_id: str, note_data: dict):
    note_data["updated_at"] = datetime.utcnow()
    result = await db.notes.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": note_data}
    )
    if result.modified_count:
        return await get_note_by_id(note_id)
    return None

async def delete_note(note_id: str):
    result = await db.notes.delete_one({"_id": ObjectId(note_id)})
    return result.deleted_count > 0