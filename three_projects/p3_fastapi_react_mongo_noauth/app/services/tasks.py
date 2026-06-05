from motor.motor_asyncio import AsyncIOMotorCollection
from app.schemas.tasks import TaskCreate, TaskUpdate, Task
from datetime import datetime
from bson import ObjectId

class TaskService:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create_task(self, task: TaskCreate) -> Task:
        task_data = task.dict()
        task_data["created_at"] = datetime.utcnow()
        task_data["updated_at"] = datetime.utcnow()
        result = await self.collection.insert_one(task_data)
        task_data["id"] = str(result.inserted_id)
        return Task(**task_data)

    async def get_task(self, task_id: str) -> Task:
        task = await self.collection.find_one({"_id": ObjectId(task_id)})
        if task:
            task["id"] = str(task["_id"])
            return Task(**task)
        return None

    async def get_tasks(self) -> list[Task]:
        tasks = []
        async for task in self.collection.find():
            task["id"] = str(task["_id"])
            tasks.append(Task(**task))
        return tasks

    async def update_task(self, task_id: str, task_update: TaskUpdate) -> Task:
        update_data = task_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        result = await self.collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": update_data}
        )
        if result.modified_count:
            updated_task = await self.collection.find_one({"_id": ObjectId(task_id)})
            updated_task["id"] = str(updated_task["_id"])
            return Task(**updated_task)
        return None

    async def delete_task(self, task_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(task_id)})
        return result.deleted_count > 0