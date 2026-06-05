from fastapi import APIRouter, HTTPException
from app.schemas.notes import NoteCreate, NoteUpdate, NoteResponse
from app.services.notes import create_note, get_notes, get_note_by_id, update_note, delete_note
from app.db.database import db

router = APIRouter()

@router.post("/", response_model=NoteResponse)
async def create_new_note(note: NoteCreate):
    return await create_note(note)

@router.get("/", response_model=list[NoteResponse])
async def read_all_notes():
    return await get_notes()

@router.get("/{note_id}", response_model=NoteResponse)
async def read_note(note_id: str):
    note = await get_note_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.put("/{note_id}", response_model=NoteResponse)
async def update_existing_note(note_id: str, note: NoteUpdate):
    updated_note = await update_note(note_id, note)
    if not updated_note:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_note

@router.delete("/{note_id}")
async def delete_existing_note(note_id: str):
    deleted = await delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"detail": "Note deleted"}