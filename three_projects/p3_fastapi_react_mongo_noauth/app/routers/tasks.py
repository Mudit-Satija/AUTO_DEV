from fastapi import APIRouter, HTTPException
from app.schemas.tasks import TaskCreate, TaskResponse
from app.services.tasks import create_task, get_tasks, get_task_by_id, update_task, delete_task
from app.db.database import db

router = APIRouter()

@router.post("/", response_model=TaskResponse)
async def create_new_task(task: TaskCreate):
    return await create_task(task)

@router.get("/", response_model=list[TaskResponse])
async def retrieve_all_tasks():
    return await get_tasks()

@router.get("/{task_id}", response_model=TaskResponse)
async def retrieve_task(task_id: str):
    task = await get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_existing_task(task_id: str, task: TaskCreate):
    updated_task = await update_task(task_id, task)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@router.delete("/{task_id}")
async def remove_task(task_id: str):
    deleted = await delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted"}