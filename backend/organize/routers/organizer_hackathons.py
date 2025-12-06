# routers/organizer_hackathons.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
import shutil
import os
import uuid

from db import get_session
from db.models import HackathonModel, OrganizerModel
from schemas.hackathon import (
    HackathonCreate, 
    HackathonUpdate, 
    HackathonResponse
)
from dependencies import get_current_organizer
from db.crud import get_hack_by_id, get_teams_with_empty_members

router = APIRouter(prefix="/organizer/hackathons", tags=["organizer_hackathons"])

# Папка для загрузки фото
UPLOAD_DIR = "uploads/hackathon_photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/", response_model=List[HackathonResponse])
async def get_my_hackathons(
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer)
):
    """Получить все хакатоны текущего организатора"""
    
    result = await session.execute(
        select(HackathonModel).where(
            HackathonModel.organizer_id == current_organizer.id
        ).order_by(HackathonModel.start_date.desc())
    )
    
    hackathons = result.scalars().all()
    return hackathons


@router.post("/", response_model=HackathonResponse, status_code=status.HTTP_201_CREATED)
async def create_hackathon(
    hackathon_data: HackathonCreate,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer)
):
    """Создать новый хакатон"""
    
    # Проверка дат
    if hackathon_data.start_date >= hackathon_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    
    # Проверка размеров команды
    if hackathon_data.min_team_size > hackathon_data.max_team_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Min team size cannot be greater than max team size"
        )
    
    # Создаем хакатон
    hackathon = HackathonModel(
        **hackathon_data.dict(),
        organizer_id=current_organizer.id
    )
    
    session.add(hackathon)
    await session.commit()
    await session.refresh(hackathon)
    
    return hackathon


@router.get("/{hackathon_id}", response_model=HackathonResponse)
async def get_hackathon(
    hackathon_id: int,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer)
):
    """Получить конкретный хакатон организатора"""
    
    hackathon = await get_hack_by_id(session, hackathon_id)
    
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    
    # Проверяем права доступа
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this hackathon"
        )
    
    return hackathon


@router.patch("/{hackathon_id}", response_model=HackathonResponse)
async def update_hackathon(
    hackathon_id: int,
    hackathon_data: HackathonUpdate,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer)
):
    """Обновить хакатон"""
    
    hackathon = await get_hack_by_id(session, hackathon_id)
    
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    
    # Проверяем права доступа
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this hackathon"
        )
    
    # Обновляем только переданные поля
    update_data = hackathon_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(hackathon, field, value)
    
    await session.commit()
    await session.refresh(hackathon)
    
    return hackathon


@router.delete("/{hackathon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hackathon(
    hackathon_id: int,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer)
):
    """Удалить хакатон"""
    
    hackathon = await get_hack_by_id(session, hackathon_id)
    
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    
    # Проверяем права доступа
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this hackathon"
        )
    
    await session.delete(hackathon)
    await session.commit()
    
    return None


@router.post("/{hackathon_id}/photo")
async def upload_hackathon_photo(
    hackathon_id: int,
    photo: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer)
):
    """Загрузить фото для хакатона"""
    
    hackathon = await get_hack_by_id(session, hackathon_id)
    
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    
    # Проверяем права доступа
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this hackathon"
        )
    
    # Проверяем тип файла
    if not photo.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Генерируем уникальное имя файла
    file_extension = photo.filename.split('.')[-1] if '.' in photo.filename else 'jpg'
    filename = f"{hackathon_id}_{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)
    
    # Обновляем путь в БД
    hackathon.photo_url = f"/uploads/hackathon_photos/{filename}"
    await session.commit()
    
    return {"photo_url": hackathon.photo_url}