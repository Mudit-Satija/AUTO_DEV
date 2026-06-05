from app.database import get_database
from bson import ObjectId
from datetime import datetime

db = get_database()

async def create_todo(todo_data: dict):
    todo_data["created_at"] = datetime.utcnow()
    todo_data["updated_at"] = datetime.utcnow()
    result = await db.todos.insert_one(todo_data)
    todo_data["_id"] = str(result.inserted_id)
    return todo_data

async def get_todos(owner: str):
    todos = []
    async for todo in db.todos.find({"owner": owner}):
        todo["_id"] = str(todo["_id"])
        todos.append(todo)
    return todos

async def get_todo_by_id(todo_id: str):
    todo = await db.todos.find_one({"_id": ObjectId(todo_id)})
    if todo:
        todo["_id"] = str(todo["_id"])
    return todo

async def update_todo(todo_id: str, todo_data: dict):
    todo_data["updated_at"] = datetime.utcnow()
    result = await db.todos.update_one(
        {"_id": ObjectId(todo_id)},
        {"$set": todo_data}
    )
    if result.modified_count:
        return await get_todo_by_id(todo_id)
    return None

async def delete_todo(todo_id: str):
    result = await db.todos.delete_one({"_id": ObjectId(todo_id)})
    return result.deleted_count > 0