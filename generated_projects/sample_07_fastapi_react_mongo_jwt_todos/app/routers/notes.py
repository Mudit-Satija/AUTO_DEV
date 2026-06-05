from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import NoteCreate, NoteOut
from app.services.notes import create_note, get_notes, get_note_by_id, update_note, delete_note
from app.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
async def create_new_note(note: NoteCreate, current_user: dict = Depends(get_current_user)):
    note_data = note.dict()
    note_data["owner"] = current_user["username"]
    return await create_note(note_data)

@router.get("/", response_model=list[NoteOut])
async def read_notes(current_user: dict = Depends(get_current_user)):
    return await get_notes(current_user["username"])

@router.get("/{note_id}", response_model=NoteOut)
async def read_note(note_id: str, current_user: dict = Depends(get_current_user)):
    note = await get_note_by_id(note_id)
    if not note or note["owner"] != current_user["username"]:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.put("/{note_id}", response_model=NoteOut)
async def update_existing_note(note_id: str, note: NoteCreate, current_user: dict = Depends(get_current_user)):
    existing_note = await get_note_by_id(note_id)
    if not existing_note or existing_note["owner"] != current_user["username"]:
        raise HTTPException(status_code=404, detail="Note not found")
    updated_note = await update_note(note_id, note.dict())
    if not updated_note:
        raise HTTPException(status_code=400, detail="Failed to update note")
    return updated_note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_note(note_id: str, current_user: dict = Depends(get_current_user)):
    note = await get_note_by_id(note_id)
    if not note or note["owner"] != current_user["username"]:
        raise HTTPException(status_code=404, detail="Note not found")
    await delete_note(note_id)
    return None