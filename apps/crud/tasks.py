from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select
from apps.models.tasks import Task, TaskCreate, TaskUpdate, TaskAssignee, Tag, TaskTag
from apps.models.users import User

async def create_task(session: Session, task_create: TaskCreate) -> Task:
    db_task = Task.from_orm(task_create)
    
    # Handle tags if provided
    if task_create.tag_names:
        tags = []
        for tag_name in task_create.tag_names:
            tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
            tags.append(tag)
        db_task.tags = tags

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    
    if task_create.assignee_ids:
        assignees = session.exec(select(User).where(User.user_id.in_(task_create.assignee_ids))).all()
        db_task.assignees = assignees
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        
    return db_task

async def get_task(session: Session, task_id: int) -> Optional[Task]:
    return session.get(Task, task_id)

async def list_tasks(
    session: Session, 
    skip: int = 0, 
    limit: int = 100,
    assignee_id: List[int] = None,
    tag_name: List[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Task]:
    query = select(Task)
    if assignee_id:
        query = query.where(Task.assignees.any(User.user_id.in_(assignee_id)))
    if tag_name:
        query = query.where(Task.tags.any(Tag.name.in_(tag_name)))
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    if start_date:
        query = query.where(Task.start_date >= start_date)
    if end_date:
        query = query.where(Task.end_date <= end_date)
    
    query = query.offset(skip).limit(limit)
    return session.exec(query).all()

async def update_task(session: Session, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
    db_task = await get_task(session, task_id)
    if not db_task:
        return None
    
    task_data = task_update.dict(exclude_unset=True)
    
    if "assignee_ids" in task_data:
        assignee_ids = task_data.pop("assignee_ids")
        if assignee_ids is not None:
            assignees = session.exec(select(User).where(User.user_id.in_(assignee_ids))).all()
            db_task.assignees = assignees

    if "tag_ids" in task_data:
        tag_ids = task_data.pop("tag_ids")
        if tag_ids is not None:
            tags = session.exec(select(Tag).where(Tag.tag_id.in_(tag_ids))).all()
            db_task.tags = tags
            
    for key, value in task_data.items():
        setattr(db_task, key, value)
        
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

async def delete_task(session: Session, task_id: int) -> Optional[Task]:
    db_task = await get_task(session, task_id)
    if not db_task:
        return None
    
    session.delete(db_task)
    session.commit()
    return db_task

async def add_assignee(session: Session, task_id: int, user_id: int) -> Optional[Task]:
    db_task = await get_task(session, task_id)
    if not db_task:
        return None
        
    user = session.get(User, user_id)
    if not user:
        return None
        
    if user not in db_task.assignees:
        db_task.assignees.append(user)
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        
    return db_task

async def bulk_update_tasks(session: Session, task_ids: List[int], updates: TaskUpdate) -> List[Task]:
    updated_tasks = []
    for task_id in task_ids:
        task = await update_task(session, task_id, updates)
        if task:
            updated_tasks.append(task)
    return updated_tasks


async def get_task_distribution(session: Session) -> List["TaskDistribution"]:
    from sqlalchemy import func
    from apps.models.tasks import TaskDistribution, TaskStatus
    
    # Query to get counts by user and status
    # We need to join User, TaskAssignee, and Task
    stmt = (
        select(
            User.user_id,
            User.username,
            Task.status,
            func.count(Task.task_id).label("count")
        )
        .join(TaskAssignee, User.user_id == TaskAssignee.user_id)
        .join(Task, TaskAssignee.task_id == Task.task_id)
        .group_by(User.user_id, User.username, Task.status)
    )
    
    results = session.exec(stmt).all()
    
    # Process results into TaskDistribution objects
    dist_map = {}
    for user_id, username, status, count in results:
        if user_id not in dist_map:
            dist_map[user_id] = TaskDistribution(user_id=user_id, username=username)
        
        if status == TaskStatus.TODO:
            dist_map[user_id].todo = count
        elif status == TaskStatus.IN_PROGRESS:
            dist_map[user_id].in_progress = count
        elif status == TaskStatus.DONE:
            dist_map[user_id].done = count
            
    return list(dist_map.values())


async def get_overdue_tasks(session: Session) -> List["UserOverdueSummary"]:
    from apps.models.tasks import UserOverdueSummary, OverdueTask, TaskStatus
    
    current_time = datetime.utcnow()
    
    # Query for overdue tasks not done
    stmt = (
        select(User, Task)
        .join(TaskAssignee, User.user_id == TaskAssignee.user_id)
        .join(Task, TaskAssignee.task_id == Task.task_id)
        .where(Task.end_date < current_time)
        .where(Task.status != TaskStatus.DONE)
        .order_by(User.username, Task.end_date)
    )
    
    results = session.exec(stmt).all()
    
    # Group by user
    user_map = {}
    for user, task in results:
        if user.user_id not in user_map:
            user_map[user.user_id] = UserOverdueSummary(
                user_id=user.user_id,
                username=user.username,
                tasks=[]
            )
        
        overdue_task = OverdueTask(
            task_id=task.task_id,
            title=task.title,
            due_date=task.end_date,
            status=task.status,
            priority=task.priority
        )
        user_map[user.user_id].tasks.append(overdue_task)
        
    return list(user_map.values())
