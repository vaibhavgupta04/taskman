from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from apps.stores.db import get_session
from apps.models.tasks import Task, TaskCreate, TaskUpdate, TaskRead, TaskStatus, TaskPriority, BulkTaskUpdate, TaskDistribution, UserOverdueSummary
from apps.crud import tasks as task_crud
from apps.auth.dependencies import get_current_user
from apps.models.users import User

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskRead)
async def create_task(
    task: TaskCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await task_crud.create_task(session, task)

@router.get("/", response_model=List[TaskRead])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    assignee_id: Optional[List[int]] = Query(None),
    tag_name: Optional[List[str]] = Query(None),
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await task_crud.list_tasks(
        session, skip, limit, assignee_id, tag_name, status, priority, start_date, end_date
    )

@router.put("/bulk", response_model=List[TaskRead])
async def bulk_update_tasks(
    bulk_update: BulkTaskUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await task_crud.bulk_update_tasks(session, bulk_update.task_ids, bulk_update.updates)

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    task = await task_crud.get_task(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int, 
    task_update: TaskUpdate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    task = await task_crud.update_task(session, task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}", response_model=TaskRead)
async def delete_task(
    task_id: int, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    task = await task_crud.delete_task(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/{task_id}/assign/{user_id}", response_model=TaskRead)
async def assign_user(
    task_id: int, 
    user_id: int, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    task = await task_crud.add_assignee(session, task_id, user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task or User not found")
    return task

@router.post("/{task_id}/subtasks", response_model=TaskRead)
async def create_subtask(
    task_id: int,
    subtask: TaskCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Ensure parent task exists
    parent_task = await task_crud.get_task(session, task_id)
    if not parent_task:
        raise HTTPException(status_code=404, detail="Parent task not found")
        
    subtask.parent_id = task_id
    return await task_crud.create_task(session, subtask)


@router.get("/distribution", response_model=List[TaskDistribution])
async def get_task_distribution(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await task_crud.get_task_distribution(session)

@router.get("/overdue", response_model=List[UserOverdueSummary])
async def get_overdue_tasks(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await task_crud.get_overdue_tasks(session)