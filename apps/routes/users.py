from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from apps.stores.db import get_session
from apps.models.users import User, UserLogin, Token
from apps.crud import users as user_crud
from apps.auth.auth import auth_manager
from apps.auth.dependencies import get_current_user, get_current_admin_user

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user: User, session: Session = Depends(get_session)):

    if user.role not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    db_user = await user_crud.get_user_by_username(session, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth_manager.get_password_hash(user.password)
    new_user = User(username=user.username, password=hashed_password, role = user.role)
    return await user_crud.create_user(session, new_user)

@router.post("/login", response_model=Token)
async def login(user: UserLogin, session: Session = Depends(get_session)):
    db_user = await user_crud.get_user_by_username(session, username=user.username)
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not active",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not db_user or not auth_manager.verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_manager.create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.delete("/users/{user_id}", response_model=User)
async def delete_user(
    user_id: int, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    db_user = await user_crud.get_user(session, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.is_active = False
    return await user_crud.update_user(session, db_user.user_id, {"is_active": False})
