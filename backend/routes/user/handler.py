import time

import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config import JWT_EXPIRE_MINUTES, SECRET_KEY, TG_BOT_TOKEN
from db import crud, get_session
from routes.user.schema import TelegramAuthPayload, UserAuthResponse
from utils import verify_telegram_auth

router = APIRouter(prefix="/api/user")


def create_jwt(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXPIRE_MINUTES * 60,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    if isinstance(token, bytes):
        token = token.decode()
    return token


@router.post("/auth")
async def telegram_auth(
    payload: TelegramAuthPayload, session: AsyncSession = Depends(get_session)
) -> UserAuthResponse:
    data = payload.model_dump()
    if not verify_telegram_auth(data, TG_BOT_TOKEN):
        raise HTTPException(status_code=400, detail="Неккоректные данные токена телеграм")

    user = crud.get_or_create_user_by_telegram(
        session=session,
        tg_id=data["id"],
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        username=data.get("username"),
        photo_url=data.get("photo_url"),
    )

    token = create_jwt(user_id=user["id"])
    return UserAuthResponse(access_token=token, token_type="bearer", user=user)
