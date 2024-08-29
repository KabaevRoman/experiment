import enum

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Status(enum.Enum):
    IN_QUEUE = 'In Queue'
    RUN = 'Run'
    Completed = 'Completed'


class Base(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)


class Task(Base):
    __tablename__ = "tasks"

    create_time = mapped_column(TIMESTAMP, server_default=func.now())
    start_time = mapped_column(TIMESTAMP, nullable=True)
    execution_time: Mapped[int | None] = mapped_column()
    status: Mapped[str] = mapped_column(default=Status.IN_QUEUE.value)
