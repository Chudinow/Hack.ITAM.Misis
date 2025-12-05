from pydantic import BaseModel, Field
from routes.user.schema import UserResponse


class TeamCreate(BaseModel):
    name: str = Field(min_length=4, max_length=64)
    hackathon_id: int
    member_ids: list[int] | None = []


class TeamUpdate(BaseModel):
    name: str = Field(min_length=4, max_length=32)
    is_completed: bool
    member_ids: list[int] | None


class TeamResponse(BaseModel):
    id: int
    name: str
    is_completed: bool
    hackathon_id: int


class TeamWithMembersResponse(TeamResponse):
    members: list[UserResponse]
