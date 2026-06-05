from motor.motor_asyncio import AsyncIOMotorCollection
from app.schemas.notes import NoteCreate, NoteUpdate, Note
from datetime import datetime
from bson import ObjectId

class NoteService:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create_note(self, note: NoteCreate) -> Note:
        note_data = note.dict()
        note_data["created_at"] = datetime.utcnow()
        note_data["updated_at"] = datetime.utcnow()
        result = await self.collection.insert_one(note_data)
        note_data["id"] = str(result.inserted_id)
        return Note(**note_data)

    async def get_note(self, note_id: str) -> Note:
        note = await self.collection.find_one({"_id": ObjectId(note_id)})
        if note:
            note["id"] = str(note["_id"])
            return Note(**note)
        return None

    async def get_notes(self) -> list[Note]:
        notes = []
        async for note in self.collection.find():
            note["id"] = str(note["_id"])
            notes.append(Note(**note))
        return notes

    async def update_note(self, note_id: str, note_update: NoteUpdate) -> Note:
        update_data = note_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        result = await self.collection.update_one(
            {"_id": ObjectId(note_id)},
            {"$set": update_data}
        )
        if result.modified_count:
            updated_note = await self.collection.find_one({"_id": ObjectId(note_id)})
            updated_note["id"] = str(updated_note["_id"])
            return Note(**updated_note)
        return None

    async def delete_note(self, note_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(note_id)})
        return result.deleted_count > 0