import time

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config import JWT_EXPIRE_MINUTES, SECRET_KEY, TG_BOT_TOKEN
from db import crud, get_session
from utils import jwt_required, verify_telegram_auth

from .schema import (
    EditProfileSchema,
    ProfileSchema,
    SkillListSchema,
    SkillSchema,
    TelegramAuthPayload,
    UserAuthResponse,
    UserSchema,
)

router = APIRouter(prefix="/api", tags=["user", "profile"])


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


@router.post("/user/auth")
async def telegram_auth(
    payload: TelegramAuthPayload, session: AsyncSession = Depends(get_session)
) -> JSONResponse:
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
    response = JSONResponse(
        UserAuthResponse(access_token=token, token_type="bearer", user=user).model_dump()
    )
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=JWT_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False,  # временно
    )
    return response


@router.get("/user/{user_id}")
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)) -> UserSchema:
    user = await crud.get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Профиль пользователя с таким id не найден.")

    return UserSchema(id=user.id, name=user.name, photo_url=user.avatar_url)


@router.get("/user/{user_id}/profile")
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


@router.put("/user/{user_profile_id}/profile")
@jwt_required
async def edit_user_profile(
    user_id: int,
    user_profile_id: int,
    edit_profile: EditProfileSchema,
    session: AsyncSession = Depends(get_session),
) -> ProfileSchema:
    if user_id != user_profile_id:
        raise HTTPException(403, detail="bla bla bla bla idi naxui")

    profile = await crud.get_profile_by_user_id(session, user_profile_id)

    if profile.about != edit_profile.about:
        profile = await crud.update_profile_about(session, profile, edit_profile.about)

    if profile.role != edit_profile.role:
        profile = await crud.update_profile_role(session, profile, edit_profile.role)

    await crud.set_profile_skills(session, profile.id, edit_profile.skills_id)

    skill_ids = await crud.get_profile_skill_ids(session, profile.id)
    skill_objs = await crud.get_skills_by_ids(session, skill_ids)

    return ProfileSchema(
        user_id=user_id,
        role=profile.role,
        about=profile.about,
        skills=[SkillSchema(id=s.id, name=s.name, type=s.type) for s in skill_objs],
    )


@router.get("/skills", response_model=SkillListSchema)
async def skills_list(session: AsyncSession = Depends(get_session)) -> SkillListSchema:
    skills = await crud.get_skills(session)
    items = [SkillSchema(id=s.id, name=s.name, type=s.type) for s in skills]
    return SkillListSchema(skills=items)


@router.get("/skill/{skill_id}", response_model=SkillSchema)
async def get_skill(skill_id: int, session: AsyncSession = Depends(get_session)) -> SkillSchema:
    skill = await crud.get_skill_by_id(session, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Навык не найден")
    return SkillSchema(id=skill.id, name=skill.name, type=skill.type)
