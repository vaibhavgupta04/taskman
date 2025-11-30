from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session
from apps.stores.db import get_session
from apps.models.tasks import TaskDistribution, TaskOverdueSummary
from apps.crud import tasks as task_crud
from apps.auth.dependencies import get_current_user
from apps.models.users import User

router = APIRouter(prefix="/features", tags=["features"])

@router.get("/task-distribution", response_model=List[TaskDistribution])
async def get_task_distribution(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await task_crud.get_task_distribution(session)

@router.get("/overdue-tasks", response_model=List[TaskOverdueSummary])
async def get_overdue_tasks(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await task_crud.get_overdue_tasks(session)
