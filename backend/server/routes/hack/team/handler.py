from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from bot.routes.invites import send_join_request, send_team_invite
from db import crud, get_session
from utils import get_current_user_id

from .schema import (
    EmptyRoleSchema,
    ParticipantSchema,
    ParticipantsListSchema,
    ProfileSchema,
    TeamCreateSchema,
    TeamResponseSchema,
    TeamWithEmptyRolesSchema,
)

router = APIRouter(prefix="/api/hack/{hack_id}", tags=["team"])


@router.post("/team/", status_code=status.HTTP_201_CREATED)
async def create_team(
    hack_id: int,
    payload: TeamCreateSchema,
    db: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> TeamResponseSchema:
    if await crud.get_team_by_hack_user(db, hack_id, user_id) is not None:
        raise HTTPException(HTTP_409_CONFLICT, detail="уже в команде/создал команду")

    team = await crud.create_team(
        session=db,
        hack_id=hack_id,
        creator_id=user_id,
        name=payload.name,
        find_roles=payload.find_roles,
        about=payload.about,
    )

    return TeamResponseSchema(id=team.id, name=team.name)


@router.get("/team/")
async def get_user_team(
    hack_id: int,
    db: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> TeamResponseSchema:
    team = await crud.get_team_by_hack_user(db, hack_id, user_id)
    if team is None:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="нету команды у тебя братиш")

    return TeamResponseSchema(id=team.id, name=team.name)


@router.get("/team/{team_id}")
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
    "/teams/search",
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
                about=team.about,
                empty_roles=empty_roles,
            )
        )
    return result


@router.get("/participants/search", response_model=ParticipantsListSchema)
async def search_ParticipantsListSchema(hack_id: int, db: AsyncSession = Depends(get_session)):
    participants = await crud.get_participants_by_hack_id(db, hack_id)

    return ParticipantsListSchema(
        participants=[
            ParticipantSchema(
                id=par.id,
                profile=ProfileSchema(
                    id=par.profile.id,
                    user_id=par.profile.user_id,
                    about=par.profile.about,
                    role=par.profile.role,
                    skills=par.profile.profile_skills,
                ),
            )
            for par in participants
        ]
    )


# приглашение участника в команду
@router.post("/team/{team_id}/invite", status_code=status.HTTP_200_OK)
async def invite_participant_to_team(
    hack_id: int,
    team_id: int,
    participant_id: int,
    db: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> dict:
    success, message = await send_team_invite(team_id, participant_id, db)
    if not success:
        raise HTTPException(HTTP_409_CONFLICT, detail=message)
    return {"detail": message}


# подача заявки на вступление в команду
@router.post("/team/{team_id}/apply", status_code=status.HTTP_200_OK)
async def apply_participant_to_team(
    hack_id: int,
    team_id: int,
    participant_id: int,
    db: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> dict:
    success, message = await send_join_request(team_id, participant_id, db)
    if not success:
        raise HTTPException(HTTP_409_CONFLICT, detail=message)
    return {"detail": message}
