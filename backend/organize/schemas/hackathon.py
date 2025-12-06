from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List


class HackathonBase(BaseModel):
    name: str = Field(max_length=255)
    description: str
    start_date: date
    end_date: date
    tags: str = ""  # В его модели tags как Text
    max_teams: int = Field(ge=1)
    min_team_size: int = Field(ge=1)
    max_team_size: int = Field(ge=1)
    photo_url: Optional[str] = None


class HackathonCreate(HackathonBase):
    pass


class HackathonUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    tags: Optional[str] = None
    max_teams: Optional[int] = Field(None, ge=1)
    min_team_size: Optional[int] = Field(None, ge=1)
    max_team_size: Optional[int] = Field(None, ge=1)
    photo_url: Optional[str] = None


class HackathonResponse(HackathonBase):
    id: int
    organizer_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Для команды и участников
class TeamMemberResponse(BaseModel):
    id: int
    user_id: Optional[int]
    role: str
    approved: bool
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TeamResponse(BaseModel):
    id: int
    name: str
    is_completed: bool
    hackathon_id: int
    members: List[TeamMemberResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ParticipantResponse(BaseModel):
    user_id: int
    name: str
    avatar_url: str
    has_team: bool
    team_name: Optional[str] = None
    role: Optional[str] = None
    skills: List[str] = []

    model_config = ConfigDict(from_attributes=True)