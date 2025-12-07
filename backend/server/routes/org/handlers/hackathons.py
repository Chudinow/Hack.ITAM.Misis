import os
import shutil
import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from db.crud import get_hack_by_id
from db.models import HackathonModel, OrganizerModel
from dependencies import get_current_organizer_cookie

from ..schemas.hackathon import (
    ErrorResponse,
    HackathonCreate,
    HackathonCreateWithPhoto,
    HackathonResponse,
    HackathonUpdate,
    HackathonUpdateWithPhoto,
    PhotoUploadResponse,
)

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
        401: {"model": ErrorResponse, "description": "Не авторизован"},
    },
)
async def get_my_hackathons(
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie),
):
    result = await session.execute(
        select(HackathonModel)
        .where(HackathonModel.organizer_id == current_organizer.id)
        .order_by(HackathonModel.start_date.desc())
    )
    hackathons = result.scalars().all()
    return hackathons


@router.post(
    "/",
    response_model=HackathonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый хакатон (JSON)",
    description="Создает новый хакатон с указанными параметрами (JSON запрос)",
    responses={
        201: {"description": "Хакатон успешно создан"},
        400: {"model": ErrorResponse, "description": "Некорректные данные (даты, размеры команд)"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
    },
)
async def create_hackathon(
    hackathon_data: HackathonCreate,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie),
):
    """Создание хакатона через JSON (без фото)"""
    if hackathon_data.start_date >= hackathon_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Дата начала должна быть раньше даты окончания",
        )

    if hackathon_data.min_team_size > hackathon_data.max_team_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Минимальный размер команды не может быть больше максимального",
        )

    hackathon = HackathonModel(
        **hackathon_data.dict(), organizer_id=current_organizer.id, photo_url=None
    )

    session.add(hackathon)
    await session.commit()
    await session.refresh(hackathon)

    return hackathon


@router.post(
    "/create-with-photo",
    response_model=HackathonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать хакатон с фото (Form Data)",
    description="""
    Создает новый хакатон с загрузкой фото в одном запросе.
    
    **Поля формы (multipart/form-data):**
    - `name`: Название хакатона (обязательно)
    - `description`: Описание хакатона (обязательно)
    - `start_date`: Дата начала в формате YYYY-MM-DD (обязательно)
    - `end_date`: Дата окончания в формате YYYY-MM-DD (обязательно)
    - `tags`: Теги через запятую (необязательно)
    - `max_teams`: Максимальное количество команд (по умолчанию 20)
    - `min_team_size`: Минимальный размер команды (по умолчанию 2)
    - `max_team_size`: Максимальный размер команды (по умолчанию 5)
    - `photo`: Файл изображения (необязательно)
    """,
    responses={
        201: {"description": "Хакатон успешно создан"},
        400: {"model": ErrorResponse, "description": "Некорректные данные"},
        401: {"model": ErrorResponse, "description": "Не авторизован"},
    },
)
async def create_hackathon_with_photo(
    name: str = Form(..., description="Название хакатона"),
    description: str = Form(..., description="Описание хакатона"),
    start_date: date = Form(..., description="Дата начала в формате YYYY-MM-DD"),
    end_date: date = Form(..., description="Дата окончания в формате YYYY-MM-DD"),
    tags: str = Form("", description="Теги через запятую"),
    max_teams: int = Form(20, ge=1, description="Максимальное количество команд"),
    min_team_size: int = Form(2, ge=1, description="Минимальный размер команды"),
    max_team_size: int = Form(5, ge=1, description="Максимальный размер команды"),
    photo: Optional[UploadFile] = File(None, description="Фото хакатона (необязательно)"),
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie),
):
    """Создание хакатона с возможностью загрузки фото через форму"""

    if start_date >= end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Дата начала должна быть раньше даты окончания",
        )

    if min_team_size > max_team_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Минимальный размер команды не может быть больше максимального",
        )

    # Создаем хакатон
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
        photo_url=None,
    )

    session.add(hackathon)
    await session.commit()
    await session.refresh(hackathon)

    # Если есть фото - загружаем
    if photo and photo.content_type and photo.content_type.startswith("image/"):
        file_extension = photo.filename.split(".")[-1] if "." in photo.filename else "jpg"
        filename = f"{hackathon.id}_{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        hackathon.photo_url = f"/uploads/hackathon_photos/{filename}"
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
        404: {"model": ErrorResponse, "description": "Хакатон не найден"},
    },
)
async def get_hackathon(
    hackathon_id: int,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie),
):
    hackathon = await get_hack_by_id(session, hackathon_id)

    if not hackathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Хакатон не найден")

    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав доступа к этому хакатону"
        )

    return hackathon


@router.patch(
    "/{hackathon_id}",
    response_model=HackathonResponse,
    summary="Обновить информацию о хакатоне (PATCH)",
    description="""
    Частично обновляет информацию о хакатоне.
    
    **Поля для обновления (все необязательные):**
    - `name`: Название хакатона
    - `description`: Описание хакатона
    - `start_date`: Дата начала
    - `end_date`: Дата окончания
    - `tags`: Теги через запятую
    - `max_teams`: Максимальное количество команд
    - `min_team_size`: Минимальный размер команды
    - `max_team_size`: Максимальный размер команды
    
    *Примечание: для обновления фото используйте отдельный эндпоинт /{hackathon_id}/photo*
    """,
    responses={
        200: {"description": "Хакатон успешно обновлен"},
        400: {"model": ErrorResponse, "description": "Некорректные данные"},
        403: {"model": ErrorResponse, "description": "Нет прав доступа к этому хакатону"},
        404: {"model": ErrorResponse, "description": "Хакатон не найден"},
    },
)
async def update_hackathon(
    hackathon_id: int,
    hackathon_data: HackathonUpdate,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie),
):
    hackathon = await get_hack_by_id(session, hackathon_id)

    if not hackathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Хакатон не найден")

    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав доступа к этому хакатону"
        )

    # Получаем только переданные поля
    update_data = hackathon_data.dict(exclude_unset=True)

    # Валидация бизнес-логики
    if "start_date" in update_data and "end_date" in update_data:
        if update_data["start_date"] >= update_data["end_date"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Дата начала должна быть раньше даты окончания",
            )

    if "min_team_size" in update_data and "max_team_size" in update_data:
        if update_data["min_team_size"] > update_data["max_team_size"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Минимальный размер команды не может быть больше максимального",
            )

    # Обновляем поля
    for field, value in update_data.items():
        if value is not None and field != "photo":  # Фото обновляем отдельно
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
        404: {"model": ErrorResponse, "description": "Хакатон не найден"},
    },
)
async def delete_hackathon(
    hackathon_id: int,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie),
):
    hackathon = await get_hack_by_id(session, hackathon_id)

    if not hackathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Хакатон не найден")

    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав доступа к этому хакатону"
        )

    # Удаляем файл фото если есть
    if hackathon.photo_url:
        photo_path = hackathon.photo_url.replace("/uploads/", "uploads/")
        if os.path.exists(photo_path):
            os.remove(photo_path)

    await session.delete(hackathon)
    await session.commit()

    return None


@router.post(
    "/{hackathon_id}/photo",
    response_model=PhotoUploadResponse,
    summary="Загрузить фото для хакатона",
    description="""
    Загружает и сохраняет фотографию для хакатона.
    
    **Формат запроса:** multipart/form-data
    **Обязательное поле:** `photo` - файл изображения
    """,
    responses={
        200: {"description": "Фото успешно загружено"},
        400: {"model": ErrorResponse, "description": "Файл не является изображением"},
        403: {"model": ErrorResponse, "description": "Нет прав доступа к этому хакатону"},
        404: {"model": ErrorResponse, "description": "Хакатон не найден"},
    },
)
async def upload_hackathon_photo(
    hackathon_id: int,
    photo: UploadFile = File(..., description="Файл изображения для хакатона"),
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie),
):
    hackathon = await get_hack_by_id(session, hackathon_id)

    if not hackathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Хакатон не найден")

    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав доступа к этому хакатону"
        )

    # Проверяем тип файла
    if not photo.content_type or not photo.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Файл должен быть изображением"
        )

    # Удаляем старое фото если есть
    if hackathon.photo_url:
        old_photo_path = hackathon.photo_url.replace("/uploads/", "uploads/")
        if os.path.exists(old_photo_path):
            os.remove(old_photo_path)

    # Генерируем уникальное имя файла
    file_extension = photo.filename.split(".")[-1] if "." in photo.filename else "jpg"
    filename = f"{hackathon_id}_{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)

    # Обновляем путь в БД
    hackathon.photo_url = f"/uploads/hackathon_photos/{filename}"
    await session.commit()

    return PhotoUploadResponse(photo_url=hackathon.photo_url, message="Фото успешно загружено")


@router.get(
    "/{hackathon_id}/photo",
    summary="Получить фото хакатона",
    description="Возвращает файл фото хакатона",
    responses={
        200: {"content": {"image/*": {}}, "description": "Фото хакатона"},
        404: {"model": ErrorResponse, "description": "Хакатон не найден или фото отсутствует"},
    },
)
async def get_hackathon_photo(hackathon_id: int, session: AsyncSession = Depends(get_session)):
    """Получение файла фото хакатона"""
    hackathon = await get_hack_by_id(session, hackathon_id)

    if not hackathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Хакатон не найден")

    if not hackathon.photo_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Фото для этого хакатона отсутствует"
        )

    # Преобразуем URL в путь к файлу
    photo_path = hackathon.photo_url.replace("/uploads/", "uploads/")

    if not os.path.exists(photo_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Файл фото не найден на сервере"
        )

    # Определяем Content-Type по расширению файла
    ext = os.path.splitext(photo_path)[1].lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
    }

    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(photo_path, media_type=media_type, filename=os.path.basename(photo_path))


@router.delete(
    "/{hackathon_id}/photo",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить фото хакатона",
    description="Удаляет фото хакатона с сервера и из базы данных",
    responses={
        204: {"description": "Фото успешно удалено"},
        403: {"model": ErrorResponse, "description": "Нет прав доступа к этому хакатону"},
        404: {"model": ErrorResponse, "description": "Хакатон не найден или фото отсутствует"},
    },
)
async def delete_hackathon_photo(
    hackathon_id: int,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie),
):
    hackathon = await get_hack_by_id(session, hackathon_id)

    if not hackathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Хакатон не найден")

    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав доступа к этому хакатону"
        )

    if not hackathon.photo_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Фото для этого хакатона отсутствует"
        )

    # Удаляем файл
    photo_path = hackathon.photo_url.replace("/uploads/", "uploads/")
    if os.path.exists(photo_path):
        os.remove(photo_path)

    # Очищаем поле в БД
    hackathon.photo_url = None
    await session.commit()

    return None
