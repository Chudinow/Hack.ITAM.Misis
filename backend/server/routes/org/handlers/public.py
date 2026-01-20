from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from db.crud import (
    get_hack_by_id,
    get_profile_by_user_id,
    get_profile_skill_ids,
    get_skills_by_ids,
    get_team_members_by_team_id,
)
from db.models import (
    HackathonModel,
    ProfileModel,
    ProfileSkillModel,
    SkillModel,
    TeamMemberModel,
    TeamModel,
    UserModel,
)

from ..schemas.hackathon import ParticipantResponse, TeamResponse

router = APIRouter(prefix="/public", tags=["public"])


@router.get(
    "/hackathons/{hackathon_id}/teams",
    response_model=List[TeamResponse],
    summary="Получить список команд хакатона (публичный)",
    description="Возвращает список команд хакатона для TG бота или публичной страницы",
    responses={
        200: {"description": "Список команд успешно получен"},
        404: {"description": "Хакатон не найден"},
    },
)
async def get_public_hackathon_teams(
    hackathon_id: int, session: AsyncSession = Depends(get_session)
):
    hackathon = await get_hack_by_id(session, hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    result = await session.execute(select(TeamModel).where(TeamModel.hackathon_id == hackathon_id))
    teams = result.scalars().all()
    response_teams = []
    for team in teams:
        members = await get_team_members_by_team_id(session, team.id)
        member_responses = []
        for member in members:
            user_info = {}
            if member.user_id:
                user_result = await session.execute(
                    select(UserModel).where(UserModel.id == member.user_id)
                )
                user = user_result.scalar_one_or_none()
                if user:
                    user_info = {"user_name": user.name, "user_avatar": user.avatar_url}
            member_response = {
                "id": member.id,
                "user_id": member.user_id,
                "role": member.role.value if hasattr(member.role, "value") else str(member.role),
                "approved": member.approved,
                **user_info,
            }
            member_responses.append(member_response)
        team_response = {
            "id": team.id,
            "name": team.name,
            "is_completed": team.is_completed,
            "hackathon_id": team.hackathon_id,
            "members": member_responses,
        }
        response_teams.append(team_response)
    return response_teams


@router.get(
    "/hackathons/{hackathon_id}/participants",
    response_model=List[ParticipantResponse],
    summary="Получить список участников хакатона (публичный)",
    description="Возвращает список участников хакатона для TG бота или публичной страницы",
    responses={
        200: {"description": "Список участников успешно получен"},
        404: {"description": "Хакатон не найден"},
    },
)
async def get_public_hackathon_participants(
    hackathon_id: int,
    team_status: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    hackathon = await get_hack_by_id(session, hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    result = await session.execute(
        select(TeamMemberModel, UserModel, TeamModel)
        .join(UserModel, TeamMemberModel.user_id == UserModel.id)
        .join(TeamModel, TeamMemberModel.team_id == TeamModel.id)
        .where(TeamModel.hackathon_id == hackathon_id)
        .where(TeamMemberModel.user_id.is_not(None))
    )
    rows = result.all()
    participants_with_teams = {}
    for member, user, team in rows:
        if user.id not in participants_with_teams:
            participants_with_teams[user.id] = {"user": user, "team": team, "role": member.role}
    participants = []
    for user_id, data in participants_with_teams.items():
        user = data["user"]
        profile = await get_profile_by_user_id(session, user.id)
        skills = []
        if profile:
            skill_ids = await get_profile_skill_ids(session, profile.id)
            skill_objs = await get_skills_by_ids(session, skill_ids)
            skills = [skill.name for skill in skill_objs]
        participant = ParticipantResponse(
            user_id=user.id,
            name=user.name,
            avatar_url=user.avatar_url,
            has_team=True,
            team_name=data["team"].name,
            role=data["role"].value if hasattr(data["role"], "value") else str(data["role"]),
            skills=skills,
        )
        participants.append(participant)
    if team_status == "without_team" or team_status is None:
        user_ids_in_teams = list(participants_with_teams.keys())
        query = select(UserModel)
        if user_ids_in_teams:
            query = query.where(UserModel.id.notin_(user_ids_in_teams))
        result = await session.execute(query)
        users_without_teams = result.scalars().all()
        for user in users_without_teams:
            if team_status == "with_team":
                continue
            profile = await get_profile_by_user_id(session, user.id)
            skills = []
            if profile:
                skill_ids = await get_profile_skill_ids(session, profile.id)
                skill_objs = await get_skills_by_ids(session, skill_ids)
                skills = [skill.name for skill in skill_objs]
            participant = ParticipantResponse(
                user_id=user.id,
                name=user.name,
                avatar_url=user.avatar_url,
                has_team=False,
                team_name=None,
                role=None,
                skills=skills,
            )
            participants.append(participant)
    if team_status == "with_team":
        participants = [p for p in participants if p.has_team]
    elif team_status == "without_team":
        participants = [p for p in participants if not p.has_team]
    return participants


@router.get(
    "/hackathons",
    summary="Получить список всех хакатонов",
    description="Возвращает список всех доступных хакатонов",
    responses={200: {"description": "Список хакатонов успешно получен"}},
)
async def get_all_hackathons(
    upcoming_only: bool = True, session: AsyncSession = Depends(get_session)
):
    today = date.today()
    if upcoming_only:
        result = await session.execute(
            select(HackathonModel).where(HackathonModel.start_date > today)
        )
    else:
        result = await session.execute(select(HackathonModel))
    hackathons = result.scalars().all()
    return [
        {
            "id": h.id,
            "name": h.name,
            "description": h.description,
            "start_date": h.start_date,
            "end_date": h.end_date,
            "photo_url": h.photo_url,
            "tags": h.tags,
        }
        for h in hackathons
    ]
