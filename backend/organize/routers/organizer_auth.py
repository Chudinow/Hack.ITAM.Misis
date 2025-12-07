from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import get_session
from db.models import OrganizerModel
from schemas.organizer import OrganizerLogin, Token, OrganizerResponse
from schemas.hackathon import ErrorResponse
from dependencies import (
    verify_password,
    create_access_token,
    get_password_hash,
    get_current_organizer_cookie
)

router = APIRouter(prefix="/organizer", tags=["organizer_auth"])

@router.post(
    "/login",
    response_model=Token,
    summary="Вход для организатора",
    description="Аутентификация организатора по логину и паролю. Устанавливает куки.",
    responses={
        200: {"description": "Успешный вход, устанавливает куки и возвращает JWT токен"},
        401: {"model": ErrorResponse, "description": "Неверные учетные данные"}
    }
)
async def organizer_login(
    response: Response,
    credentials: OrganizerLogin,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(OrganizerModel).where(OrganizerModel.login == credentials.login)
    )
    organizer = result.scalar_one_or_none()
    if not organizer or not verify_password(credentials.password, organizer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    access_token = create_access_token(
        data={"sub": str(organizer.id), "role": "organizer"}
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        samesite="lax",
        secure=False
    )
    response.set_cookie(
        key="user_id",
        value=str(organizer.id),
        max_age=1800,
        samesite="lax"
    )
    organizer_response = OrganizerResponse(
        id=organizer.id,
        login=organizer.login,
        created_at=organizer.created_at
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        organizer=organizer_response
    )

@router.post(
    "/register",
    response_model=Token,
    summary="Регистрация нового организатора",
    description="Создает нового организатора с указанными учетными данными. Возвращает JWT токен.",
    responses={
        200: {"description": "Организатор успешно зарегистрирован"},
        400: {"model": ErrorResponse, "description": "Организатор с таким логином уже существует"},
        401: {"model": ErrorResponse, "description": "Не авторизован"}
    }
)
async def organizer_register(
    credentials: OrganizerLogin,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(OrganizerModel).where(OrganizerModel.login == credentials.login)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organizer with this login already exists"
        )
    organizer = OrganizerModel(
        login=credentials.login,
        password_hash=get_password_hash(credentials.password)
    )
    session.add(organizer)
    await session.commit()
    await session.refresh(organizer)
    access_token = create_access_token(
        data={"sub": str(organizer.id), "role": "organizer"}
    )
    organizer_response = OrganizerResponse(
        id=organizer.id,
        login=organizer.login,
        created_at=organizer.created_at
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        organizer=organizer_response
    )

@router.get(
    "/me",
    response_model=OrganizerResponse,
    summary="Получить информацию о текущем организаторе",
    description="Возвращает информацию о текущем аутентифицированном организаторе",
    responses={
        200: {"description": "Информация об организаторе успешно получена"},
        401: {"model": ErrorResponse, "description": "Не авторизован"}
    }
)
async def get_current_user(
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie)
):
    return OrganizerResponse(
        id=current_organizer.id,
        login=current_organizer.login,
        created_at=current_organizer.created_at
    )

@router.post(
    "/logout",
    summary="Выход",
    description="Удаляет аутентификационные куки",
    responses={
        200: {"description": "Успешный выход"}
    }
)
async def organizer_logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="user_id")
    return {"message": "Logged out successfully"}