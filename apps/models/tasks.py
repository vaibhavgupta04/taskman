from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from apps.models.users import User

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskAssignee(SQLModel, table=True):
    task_id: Optional[int] = Field(default=None, foreign_key="task.task_id", primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.user_id", primary_key=True)

class Task(SQLModel, table=True):
    task_id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.TODO)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    due_date: Optional[datetime] = None
    parent_id: Optional[int] = Field(default=None, foreign_key="task.task_id")
    
    # Relationships
    assignees: List[User] = Relationship(link_model=TaskAssignee)
    parent: Optional["Task"] = Relationship(back_populates="subtasks", sa_relationship_kwargs={"remote_side": "Task.task_id"})
    subtasks: List["Task"] = Relationship(back_populates="parent")

class TaskCreate(SQLModel):
    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    parent_id: Optional[int] = None
    assignee_ids: Optional[List[int]] = []

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    parent_id: Optional[int] = None
    assignee_ids: Optional[List[int]] = None

class TaskRead(SQLModel):
    task_id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    parent_id: Optional[int]
    assignees: List[User]
