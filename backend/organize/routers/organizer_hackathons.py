from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
import shutil
import os
import uuid
from datetime import date
from db import get_session
from db.models import HackathonModel, OrganizerModel
from schemas.hackathon import (
    HackathonCreate,
    HackathonUpdate,
    HackathonResponse,
    ErrorResponse
)
from dependencies import get_current_organizer_cookie
from db.crud import get_hack_by_id

router = APIRouter(prefix="/organizer/hackathons", tags=["organizer_hackathons"])

UPLOAD_DIR = "uploads/hackathon_photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get(
    "/",
    response_model=List[HackathonResponse],
    summary="Получить все хакатоны организатора",
    description="Возвращает список всех хакатонов, созданных текущим организатором",
    responses={
        200: {"description": "Список хакатонов успешно получен"},
        401: {"model": ErrorResponse, "description": "Не авторизован"}
    }
)
async def get_my_hackathons(
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie)
):
    result = await session.execute(
        select(HackathonModel).where(
            HackathonModel.organizer_id == current_organizer.id
        ).order_by(HackathonModel.start_date.desc())
    )
    hackathons = result.scalars().all()
    return hackathons

@router.post(
    "/",
    response_model=HackathonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый хакатон",
    description="Создает новый хакатон с указанными параметрами",
    responses={
        201: {"description": "Хакатон успешно создан"},
        400: {"model": ErrorResponse, "description": "Некорректные данные (даты, размеры команд)"},
        401: {"model": ErrorResponse, "description": "Не авторизован"}
    }
)
async def create_hackathon(
    hackathon_data: HackathonCreate,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie)
):
    if hackathon_data.start_date >= hackathon_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    if hackathon_data.min_team_size > hackathon_data.max_team_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Min team size cannot be greater than max team size"
        )
    hackathon = HackathonModel(
        **hackathon_data.dict(),
        organizer_id=current_organizer.id
    )
    session.add(hackathon)
    await session.commit()
    await session.refresh(hackathon)
    return hackathon

@router.post(
    "/create-with-photo",
    response_model=HackathonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать хакатон с фото",
    description="Создает новый хакатон с загрузкой фото в одном запросе",
    responses={
        201: {"description": "Хакатон успешно создан"},
        400: {"model": ErrorResponse, "description": "Некорректные данные"},
        401: {"model": ErrorResponse, "description": "Не авторизован"}
    }
)
async def create_hackathon_with_photo(
    name: str = Form(...),
    description: str = Form(...),
    start_date: date = Form(...),
    end_date: date = Form(...),
    tags: str = Form(""),
    max_teams: int = Form(20),
    min_team_size: int = Form(2),
    max_team_size: int = Form(5),
    photo: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie)
):
    if start_date >= end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Дата начала должна быть раньше даты окончания"
        )
    if min_team_size > max_team_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Минимальный размер команды не может быть больше максимального"
        )
    hackathon = HackathonModel(
        name=name,
        description=description,
        start_date=start_date,
        end_date=end_date,
        tags=tags,
        max_teams=max_teams,
        min_team_size=min_team_size,
        max_team_size=max_team_size,
        organizer_id=current_organizer.id,
        photo_url=None
    )
    session.add(hackathon)
    await session.commit()
    await session.refresh(hackathon)
    photo_url = None
    if photo and photo.content_type.startswith('image/'):
        file_extension = photo.filename.split('.')[-1] if '.' in photo.filename else 'jpg'
        filename = f"{hackathon.id}_{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        photo_url = f"/uploads/hackathon_photos/{filename}"
        hackathon.photo_url = photo_url
        await session.commit()
    return hackathon

@router.get(
    "/{hackathon_id}",
    response_model=HackathonResponse,
    summary="Получить хакатон по ID",
    description="Возвращает информацию о конкретном хакатоне по его ID",
    responses={
        200: {"description": "Хакатон успешно получен"},
        403: {"model": ErrorResponse, "description": "Нет прав доступа к этому хакатону"},
        404: {"model": ErrorResponse, "description": "Хакатон не найден"}
    }
)
async def get_hackathon(
    hackathon_id: int,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie)
):
    hackathon = await get_hack_by_id(session, hackathon_id)
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this hackathon"
        )
    return hackathon

@router.patch(
    "/{hackathon_id}",
    response_model=HackathonResponse,
    summary="Обновить информацию о хакатоне",
    description="Частично обновляет информацию о хакатоне (PATCH запрос)",
    responses={
        200: {"description": "Хакатон успешно обновлен"},
        400: {"model": ErrorResponse, "description": "Некорректные данные"},
        403: {"model": ErrorResponse, "description": "Нет прав доступа к этому хакатону"},
        404: {"model": ErrorResponse, "description": "Хакатон не найден"}
    }
)
async def update_hackathon(
    hackathon_id: int,
    hackathon_data: HackathonUpdate,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie)
):
    hackathon = await get_hack_by_id(session, hackathon_id)
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this hackathon"
        )
    update_data = hackathon_data.dict(exclude_unset=True)
    if "start_date" in update_data and "end_date" in update_data:
        if update_data["start_date"] >= update_data["end_date"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before end date"
            )
    if "min_team_size" in update_data and "max_team_size" in update_data:
        if update_data["min_team_size"] > update_data["max_team_size"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Min team size cannot be greater than max team size"
            )
    for field, value in update_data.items():
        setattr(hackathon, field, value)
    await session.commit()
    await session.refresh(hackathon)
    return hackathon

@router.delete(
    "/{hackathon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить хакатон",
    description="Удаляет хакатон и все связанные с ним данные",
    responses={
        204: {"description": "Хакатон успешно удален"},
        403: {"model": ErrorResponse, "description": "Нет прав доступа к этому хакатону"},
        404: {"model": ErrorResponse, "description": "Хакатон не найден"}
    }
)
async def delete_hackathon(
    hackathon_id: int,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie)
):
    hackathon = await get_hack_by_id(session, hackathon_id)
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this hackathon"
        )
    await session.delete(hackathon)
    await session.commit()
    return None

@router.post(
    "/{hackathon_id}/photo",
    summary="Загрузить фото для хакатона",
    description="Загружает и сохраняет фотографию для хакатона",
    responses={
        200: {"description": "Фото успешно загружено"},
        400: {"model": ErrorResponse, "description": "Файл не является изображением"},
        403: {"model": ErrorResponse, "description": "Нет прав доступа к этому хакатону"},
        404: {"model": ErrorResponse, "description": "Хакатон не найден"}
    }
)
async def upload_hackathon_photo(
    hackathon_id: int,
    photo: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie)
):
    hackathon = await get_hack_by_id(session, hackathon_id)
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this hackathon"
        )
    if not photo.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    file_extension = photo.filename.split('.')[-1] if '.' in photo.filename else 'jpg'
    filename = f"{hackathon_id}_{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)
    hackathon.photo_url = f"/uploads/hackathon_photos/{filename}"
    await session.commit()
    return {"photo_url": hackathon.photo_url, "message": "Photo uploaded successfully"}