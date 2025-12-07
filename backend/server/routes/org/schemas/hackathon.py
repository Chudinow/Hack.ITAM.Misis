# schemas/hackathon.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List
from fastapi import UploadFile


class HackathonBase(BaseModel):
    name: str = Field(..., max_length=255, description="Название хакатона")
    description: str = Field(..., description="Описание хакатона")
    start_date: date = Field(..., description="Дата начала хакатона")
    end_date: date = Field(..., description="Дата окончания хакатона")
    tags: str = Field(default="", description="Теги хакатона (через запятую)")
    max_teams: int = Field(default=20, ge=1, description="Максимальное количество команд")
    min_team_size: int = Field(default=2, ge=1, description="Минимальный размер команды")
    max_team_size: int = Field(default=5, ge=1, description="Максимальный размер команды")


class HackathonCreate(HackathonBase):
    pass


class HackathonCreateWithPhoto(BaseModel):
    """Схема для создания хакатона с фото (multipart/form-data)"""
    name: str = Field(..., max_length=255)
    description: str = Field(...)
    start_date: date = Field(...)
    end_date: date = Field(...)
    tags: Optional[str] = Field(default="")
    max_teams: int = Field(default=20, ge=1)
    min_team_size: int = Field(default=2, ge=1)
    max_team_size: int = Field(default=5, ge=1)
    photo: Optional[UploadFile] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class HackathonUpdate(BaseModel):
    """Схема для обновления хакатона (PATCH) - все поля optional"""
    name: Optional[str] = Field(None, max_length=255, description="Название хакатона")
    description: Optional[str] = Field(None, description="Описание хакатона")
    start_date: Optional[date] = Field(None, description="Дата начала хакатона")
    end_date: Optional[date] = Field(None, description="Дата окончания хакатона")
    tags: Optional[str] = Field(None, description="Теги хакатона")
    max_teams: Optional[int] = Field(None, ge=1, description="Максимальное количество команд")
    min_team_size: Optional[int] = Field(None, ge=1, description="Минимальный размер команды")
    max_team_size: Optional[int] = Field(None, ge=1, description="Максимальный размер команды")
    photo: Optional[UploadFile] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class HackathonUpdateWithPhoto(BaseModel):
    """Схема для обновления фото хакатона"""
    photo: UploadFile

    model_config = ConfigDict(arbitrary_types_allowed=True)


class HackathonResponse(HackathonBase):
    id: int
    organizer_id: int
    photo_url: Optional[str] = Field(None, description="URL фото хакатона")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


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


class AnalyticsResponse(BaseModel):
    hackathon_id: int
    hackathon_name: str
    total_teams: int
    total_participants: int
    incomplete_teams: int
    team_completion_rate: float
    max_teams: int
    team_size_range: dict
    role_distribution: dict
    remaining_slots: int
    registration_status: str
    days_until_start: int
    average_team_size: float

    model_config = ConfigDict(from_attributes=True)


class TeamApproveResponse(BaseModel):
    team_id: int
    approved: bool
    message: str
    team_name: str
    total_members: int
    approved_members: int

    model_config = ConfigDict(from_attributes=True)


class AssignParticipantResponse(BaseModel):
    success: bool
    message: str
    team_id: int
    team_name: str
    user_id: int
    user_name: str
    role: str
    team_completed: bool
    team_size_before: int
    team_size_after: int

    model_config = ConfigDict(from_attributes=True)


class CSVExportResponse(BaseModel):
    filename: str
    content_type: str = "text/csv"
    message: str = "CSV file generated successfully"


class PhotoUploadResponse(BaseModel):
    photo_url: str
    message: str = "Photo uploaded successfully"


class ErrorResponse(BaseModel):
    detail: str
    status_code: int