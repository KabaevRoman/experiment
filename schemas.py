from datetime import datetime

from pydantic import BaseModel


class TaskSchema(BaseModel):
    id: int
    status: str
    create_time: datetime
    start_time: datetime | None
    execution_time: int | None
