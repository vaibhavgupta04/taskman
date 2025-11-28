from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import func, join
from sqlmodel import Session, and_, or_, select
from apps.models import users



async def get_user_by_username(session: Session, username: str):
    stmt = select(users.User).where(users.User.username == username)
    return session.exec(stmt).first()


async def create_user(session: Session, user: users.User):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

async def delete_user(session: Session, user: users.User):
    session.delete(user)
    session.commit()
    session.refresh()
    return user

async def get_user(session: Session, user_id: int) -> Optional[users.User]:
    stmt = select(users.User).where(users.User.user_id == user_id)
    return session.exec(stmt).first()


async def get_user_by_username(session: Session, username: str) -> Optional[users.User]:
    stmt = select(users.User).where(users.User.username == username)
    return session.exec(stmt).first()


async def create_user(session: Session, user_data: Union[users.User, Dict[str, Any]]) -> users.User:
    if isinstance(user_data, users.User):
        session.add(user_data)
        session.commit()
        session.refresh(user_data)
        return user_data

    db_user = users.User(**user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


async def update_user(session: Session, user_id: int, user_update: Union[users.User, Dict[str, Any]]) -> Optional[users.User]:
    db_user = await get_user(session, user_id)
    if not db_user:
        return None

    if isinstance(user_update, users.User):
        update_data = user_update.dict(exclude_unset=True)
    else:
        # keep only provided keys (ignore None)
        update_data = {k: v for k, v in user_update.items() if v is not None}

    for key, value in update_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


async def delete_user_by_id(session: Session, user_id: int) -> Optional[users.User]:
    db_user = await get_user(session, user_id)
    if not db_user:
        return None
    session.delete(db_user)
    session.commit()
    return db_user


async def delete_user(session: Session, user: users.User) -> users.User:
    session.delete(user)
    session.commit()
    return user
