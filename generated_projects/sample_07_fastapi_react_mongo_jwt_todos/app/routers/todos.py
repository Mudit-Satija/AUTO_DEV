from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import TodoCreate, TodoOut
from app.services.todos import create_todo, get_todos, get_todo_by_id, update_todo, delete_todo
from app.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
async def create_new_todo(todo: TodoCreate, current_user: dict = Depends(get_current_user)):
    todo_data = todo.dict()
    todo_data["owner"] = current_user["username"]
    return await create_todo(todo_data)

@router.get("/", response_model=list[TodoOut])
async def read_todos(current_user: dict = Depends(get_current_user)):
    return await get_todos(current_user["username"])

@router.get("/{todo_id}", response_model=TodoOut)
async def read_todo(todo_id: str, current_user: dict = Depends(get_current_user)):
    todo = await get_todo_by_id(todo_id)
    if not todo or todo["owner"] != current_user["username"]:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.put("/{todo_id}", response_model=TodoOut)
async def update_existing_todo(todo_id: str, todo: TodoCreate, current_user: dict = Depends(get_current_user)):
    existing_todo = await get_todo_by_id(todo_id)
    if not existing_todo or existing_todo["owner"] != current_user["username"]:
        raise HTTPException(status_code=404, detail="Todo not found")
    updated_todo = await update_todo(todo_id, todo.dict())
    if not updated_todo:
        raise HTTPException(status_code=400, detail="Failed to update todo")
    return updated_todo

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_todo(todo_id: str, current_user: dict = Depends(get_current_user)):
    todo = await get_todo_by_id(todo_id)
    if not todo or todo["owner"] != current_user["username"]:
        raise HTTPException(status_code=404, detail="Todo not found")
    await delete_todo(todo_id)
    return None