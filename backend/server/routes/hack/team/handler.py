from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import crud, get_session

from .schema import (
    EmptyRoleSchema,
    TeamCreateSchema,
    TeamMemberCreateSchema,
    TeamMemberResponseSchema,
    TeamResponseSchema,
    TeamWithEmptyRolesSchema,
)

router = APIRouter(prefix="/api/hack/{hack_id}/team", tags=["team"])

# капитаном команды будет тот человек, который первый в списке участников, т.е. тот, кто ее регистрировал
# менять состав может только капитан
# если айди у мембера не указан, значит команда ищет человека с такой ролью


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_team(
    hack_id: int, payload: TeamCreateSchema, db: AsyncSession = Depends(get_session)
) -> TeamResponseSchema:
    team, members = await crud.create_team_with_members(
        session=db,
        name=payload.name,
        hack_id=payload.hackathon_id,
        member_ids=[member.user_id for member in payload.member_ids],
        roles=[member.role for member in payload.member_ids],
        is_completed=payload.is_completed,
    )

    return TeamResponseSchema(
        id=team.id,
        name=team.name,
        hackathon_id=team.hackathon_id,
        is_completed=team.is_completed,
        members=members,
    )


@router.get("/{team_id}")
async def get_team(
    hack_id: int, team_id: int, db: AsyncSession = Depends(get_session)
) -> TeamResponseSchema:
    team = await crud.get_team_by_id(db, team_id)
    if not team:
        raise HTTPException(404, detail="Нету такой еблан")

    members = await crud.get_team_members_by_team_id(db, team_id)
    return TeamResponseSchema(
        id=team.id,
        name=team.name,
        hackathon_id=team.hackathon_id,
        is_completed=team.is_completed,
        members=members,
    )


@router.get(
    "/search/empty",
    response_model=list[TeamWithEmptyRolesSchema],
)
async def search_teams_with_empty_members(hack_id: int, db: AsyncSession = Depends(get_session)):
    teams_with_empty = await crud.get_teams_with_empty_members(db, hackathon_id=hack_id)
    result = []
    for item in teams_with_empty:
        team = item["team"]
        empty_roles = [EmptyRoleSchema(role=member.role) for member in item["members"]]
        result.append(
            TeamWithEmptyRolesSchema(
                id=team.id,
                name=team.name,
                hackathon_id=team.hackathon_id,
                is_completed=team.is_completed,
                empty_roles=empty_roles,
            )
        )
    return result
