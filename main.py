from fastapi import FastAPI
from fastapi_filter import FilterDepends
from starlette import status

from database import redis
from repository import TaskFilter, TaskRepositoryDep
from schemas import TaskSchema

app = FastAPI()


@app.get('/tasks/{task_id}', response_model=TaskSchema, status_code=status.HTTP_200_OK)
async def get_task(
    repo: TaskRepositoryDep,
    task_id: int,
):
    return await repo.get(task_id)


@app.get('/tasks', response_model=list[TaskSchema], status_code=status.HTTP_200_OK)
async def get_tasks(
    repo: TaskRepositoryDep,
    task_filter: TaskFilter = FilterDepends(TaskFilter),
    offset: int = 0,
    limit: int = 100,
):
    return await repo.get_list(task_filter, offset, limit)


@app.post("/tasks", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
async def create_task(repo: TaskRepositoryDep):
    task = await repo.create()
    redis.publish('create_task', task.id)
    return task
