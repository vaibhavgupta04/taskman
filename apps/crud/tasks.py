from typing import List, Optional
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
    status: Optional[str] = None,
    priority: Optional[str] = None
) -> List[Task]:
    query = select(Task)
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    
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
        # We create a new copy of updates for each task to avoid side effects if update_task modifies it
        # Although update_task uses .dict(exclude_unset=True), so it should be fine.
        # But we need to be careful if we wanted to support partial success. 
        # For now, we'll try to update all.
        task = await update_task(session, task_id, updates)
        if task:
            updated_tasks.append(task)
    return updated_tasks
