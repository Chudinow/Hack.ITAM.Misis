# routers/organizer_auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db import get_session
from db.models import OrganizerModel
from schemas.organizer import OrganizerLogin, Token
from dependencies import (
    verify_password, 
    create_access_token, 
    get_password_hash,
    get_current_organizer
)

router = APIRouter(prefix="/organizer", tags=["organizer_auth"])


@router.post("/login", response_model=Token)
async def organizer_login(
    credentials: OrganizerLogin,
    session: AsyncSession = Depends(get_session)
):
    """Вход для организатора"""
    
    # Ищем организатора по логину (в его модели поле login, не email)
    result = await session.execute(
        select(OrganizerModel).where(OrganizerModel.login == credentials.login)
    )
    organizer = result.scalar_one_or_none()
    
    if not organizer or not verify_password(credentials.password, organizer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Создаем токен
    access_token = create_access_token(
        data={"sub": str(organizer.id), "role": "organizer"}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "organizer": organizer
    }


@router.post("/register", response_model=Token)
async def organizer_register(
    credentials: OrganizerLogin,
    session: AsyncSession = Depends(get_session)
):
    """Регистрация нового организатора"""
    
    # Проверяем, нет ли уже такого логина
    result = await session.execute(
        select(OrganizerModel).where(OrganizerModel.login == credentials.login)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organizer with this login already exists"
        )
    
    # Создаем нового организатора
    organizer = OrganizerModel(
        login=credentials.login,
        password_hash=get_password_hash(credentials.password)
    )
    
    session.add(organizer)
    await session.commit()
    await session.refresh(organizer)
    
    # Создаем токен
    access_token = create_access_token(
        data={"sub": str(organizer.id), "role": "organizer"}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "organizer": organizer
    }


@router.get("/me")
async def get_current_user(
    current_organizer: OrganizerModel = Depends(get_current_organizer)
):
    """Получить информацию о текущем организаторе"""
    return current_organizer