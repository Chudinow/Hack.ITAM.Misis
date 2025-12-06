from pydantic import BaseModel

from db.models import SkillType


class TelegramAuthPayload(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str


class UserAuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserSchema(BaseModel):
    id: int
    name: str
    photo_url: str


class EditProfileSchema(BaseModel):
    user_id: int
    about: str | None = None
    skills_id: list[int]


class SkillSchema(BaseModel):
    id: int
    name: str
    type: SkillType


class SkillListSchema(BaseModel):
    skills: list[SkillSchema]


class ProfileSchema(BaseModel):
    id: int
    user_id: int
    about: str
    skills: list[SkillSchema]
