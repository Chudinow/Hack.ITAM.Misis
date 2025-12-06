import time

import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config import JWT_EXPIRE_MINUTES, SECRET_KEY, TG_BOT_TOKEN
from db import crud, get_session
from utils import verify_telegram_auth

from .schema import (
    EditProfileSchema,
    ProfileSchema,
    SkillListSchema,
    SkillSchema,
    TelegramAuthPayload,
    UserAuthResponse,
    UserSchema,
)

router = APIRouter(prefix="/api/user", tags=["user", "profile"])


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


@router.get("/{user_id}")
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)) -> UserSchema:
    user = await crud.get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Профиль пользователя с таким id не найден.")

    return UserSchema(id=user.id, name=user.name, photo_url=user.avatar_url)


@router.get("/{user_id}/profile")
async def get_profile(user_id: int, session: AsyncSession = Depends(get_session)) -> ProfileSchema:
    user = await crud.get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Профиль пользователя с таким id не найден.")

    profile = await crud.get_profile_by_user_id(session, user_id)

    skill_ids = await crud.get_profile_skill_ids(session, profile.id)
    skill_objs = await crud.get_skills_by_ids(session, skill_ids)

    return ProfileSchema(
        id=profile.id,
        user_id=profile.user_id,
        about=profile.about,
        skills=[SkillSchema(id=s.id, name=s.name, type=s.type) for s in skill_objs],
    )


@router.put("/{user_id}/profile")
async def edit_user_profile(
    user_id: int, edit_profile: EditProfileSchema, session: AsyncSession = Depends(get_session)
) -> ProfileSchema:
    profile = await crud.get_profile_by_user_id(session, user_id)

    if profile.about != edit_profile.about:
        profile = await crud.update_profile_about(session, profile, edit_profile.about)

    await crud.set_profile_skills(session, profile.id, edit_profile.skills_id)

    skill_ids = await crud.get_profile_skill_ids(session, profile.id)
    skill_objs = await crud.get_skills_by_ids(session, skill_ids)

    return ProfileSchema(
        user_id=edit_profile.user_id,
        about=profile.about,
        skills=[SkillSchema(id=s.id, name=s.name, type=s.type) for s in skill_objs],
    )


@router.get("/profile/skills", response_model=SkillListSchema)
async def skills_list(session: AsyncSession = Depends(get_session)) -> SkillListSchema:
    skills = await crud.get_skills(session)
    items = [SkillSchema(id=s.id, name=s.name, type=s.type) for s in skills]
    return SkillListSchema(skills=items)


@router.get("/profile/skills/{skill_id}", response_model=SkillSchema)
async def get_skill(skill_id: int, session: AsyncSession = Depends(get_session)) -> SkillSchema:
    skill = await crud.get_skill_by_id(session, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Навык не найден")
    return SkillSchema(id=skill.id, name=skill.name, type=skill.type)
