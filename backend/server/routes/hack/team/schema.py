from pydantic import BaseModel, Field

from db.models import RoleType

from ...user.schema import ProfileSchema, UserSchema


class TeamMemberCreateSchema(BaseModel):
    user_id: int
    role: RoleType


class TeamCreateSchema(BaseModel):
    name: str = Field(min_length=4, max_length=64)
    find_roles: list[RoleType]
    about: str

    # member_ids: list[TeamMemberCreateSchema] бля поле просто иди нахуй
    # is_completed: bool всегда


class TeamMemberResponseSchema(BaseModel):
    id: int
    user_id: int
    role: RoleType
    approved: bool


class TeamResponseSchema(BaseModel):
    id: int
    name: str


class EmptyRoleSchema(BaseModel):
    role: RoleType


class TeamWithEmptyRolesSchema(BaseModel):
    id: int
    name: str
    hackathon_id: int
    about: str
    empty_roles: list[EmptyRoleSchema]


class ParticipantSchema(BaseModel):
    id: int
    profile: ProfileSchema


class ParticipantsListSchema(BaseModel):
    participants: list[ParticipantSchema]
