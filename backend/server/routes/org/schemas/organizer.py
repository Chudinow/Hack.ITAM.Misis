from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrganizerBase(BaseModel):
    login: str = Field(min_length=3, max_length=128)
    # Примечание: в его модели используется login, не email


class OrganizerCreate(OrganizerBase):
    password: str = Field(min_length=6)


class OrganizerLogin(BaseModel):
    login: str
    password: str


class OrganizerResponse(OrganizerBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    organizer: OrganizerResponse
