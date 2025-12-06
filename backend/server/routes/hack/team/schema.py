from pydantic import BaseModel, Field

from db.models import RoleType

from ...user.schema import UserSchema


class TeamMemberCreateSchema(BaseModel):
    user_id: int
    role: RoleType


class TeamCreateSchema(BaseModel):
    name: str = Field(min_length=4, max_length=64)
    hackathon_id: int
    member_ids: list[TeamMemberCreateSchema]
    is_completed: bool


class TeamMemberResponseSchema(BaseModel):
    id: int
    user_id: int
    role: RoleType
    approved: bool


class TeamResponseSchema(BaseModel):
    id: int
    name: str
    hackathon_id: int
    is_completed: bool
    members: list[TeamMemberResponseSchema]


class EmptyRoleSchema(BaseModel):
    role: RoleType


class TeamWithEmptyRolesSchema(BaseModel):
    id: int
    name: str
    hackathon_id: int
    is_completed: bool
    empty_roles: list[EmptyRoleSchema]
