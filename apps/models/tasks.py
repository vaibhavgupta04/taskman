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


class TaskTag(SQLModel, table=True):
    task_id: Optional[int] = Field(default=None, foreign_key="task.task_id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.tag_id", primary_key=True)


class Tag(SQLModel, table=True):
    tag_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    tasks: List["Task"] = Relationship(back_populates="tags", link_model=TaskTag)


class TaskDependency(SQLModel, table=True):
    blocker_id: Optional[int] = Field(default=None, foreign_key="task.task_id", primary_key=True)
    blocked_id: Optional[int] = Field(default=None, foreign_key="task.task_id", primary_key=True)


class Task(SQLModel, table=True):
    task_id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.TODO)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    parent_id: Optional[int] = Field(default=None, foreign_key="task.task_id")
    
    assignees: List[User] = Relationship(link_model=TaskAssignee)
    tags: List[Tag] = Relationship(back_populates="tasks", link_model=TaskTag)
    
    parent: Optional["Task"] = Relationship(
        back_populates="subtasks",
        sa_relationship_kwargs={"remote_side": "Task.task_id"}
    )
    subtasks: List["Task"] = Relationship(back_populates="parent")
    
    blockers: List["Task"] = Relationship(
        link_model=TaskDependency,
        sa_relationship_kwargs={
            "primaryjoin": "Task.task_id==TaskDependency.blocked_id",
            "secondaryjoin": "Task.task_id==TaskDependency.blocker_id"
        }
    )
    blocked_by: List["Task"] = Relationship(
        link_model=TaskDependency,
        sa_relationship_kwargs={
            "primaryjoin": "Task.task_id==TaskDependency.blocker_id",
            "secondaryjoin": "Task.task_id==TaskDependency.blocked_id"
        }
    )

class TaskCreate(SQLModel):
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    start_date: datetime
    end_date: datetime
    parent_id: Optional[int] = None
    assignee_ids: Optional[List[int]] = []
    tag_names: Optional[List[str]] = []


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    parent_id: Optional[int] = None
    assignee_ids: Optional[List[int]] = None
    tag_names: Optional[List[str]] = None


class TaskRead(SQLModel):
    task_id: int
    title: str
    description: Optional[str]
    status: Optional[TaskStatus]
    priority: Optional[TaskPriority]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime] 
    parent_id: Optional[int]
    assignees: List[User]
    tags: List[Tag]

class BulkTaskUpdate(SQLModel):
    task_ids: List[int]
    updates: TaskUpdate


class TaskDistribution(SQLModel):
    user_id: int
    username: str
    todo: int = 0
    in_progress: int = 0
    done: int = 0


class OverdueTask(SQLModel):
    task_id: int
    title: str
    due_date: datetime
    status: TaskStatus
    priority: TaskPriority


class TaskOverdueSummary(SQLModel):
    user_id: int
    username: str
    tasks: List[OverdueTask]