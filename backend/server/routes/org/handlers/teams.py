import csv
import tempfile
from datetime import date, datetime
from io import StringIO
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from db.crud import (
    count_teams_for_hack,
    get_hack_by_id,
    get_profile_by_user_id,
    get_profile_skill_ids,
    get_skills_by_ids,
    get_team_by_id,
    get_team_members_by_team_id,
    get_users_by_ids,
)
from db.models import (
    HackathonModel,
    OrganizerModel,
    ProfileModel,
    RoleType,
    SkillModel,
    TeamMemberModel,
    TeamModel,
    UserModel,
)
from dependencies import get_current_organizer_cookie

from ..schemas.hackathon import (
    AnalyticsResponse,
    AssignParticipantResponse,
    ErrorResponse,
    ParticipantResponse,
    TeamApproveResponse,
    TeamResponse,
)

router = APIRouter(prefix="/organizer/hackathons/{hackathon_id}", tags=["organizer_teams"])


@router.get(
    "/teams",
    response_model=List[TeamResponse],
    summary="Получить все команды хакатона",
    description="Возвращает список всех команд хакатона с информацией об участниках",
    responses={
        200: {"description": "Список команд успешно получен"},
        403: {"model": ErrorResponse, "description": "Нет прав доступа к хакатону"},
        404: {"model": ErrorResponse, "description": "Хакатон не найден"},
    },
)
async def get_hackathon_teams(
    hackathon_id: int,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie),
):
    hackathon = await get_hack_by_id(session, hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this hackathon"
        )
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
    "/participants",
    response_model=List[ParticipantResponse],
    summary="Получить участников хакатона",
    description="Возвращает участников хакатона с фильтрацией по наличию команды",
    responses={
        200: {"description": "Список участников успешно получен"},
        400: {"model": ErrorResponse, "description": "Некорректный параметр team_status"},
        403: {"model": ErrorResponse, "description": "Нет прав доступа к хакатону"},
        404: {"model": ErrorResponse, "description": "Хакатон не найден"},
    },
)
async def get_hackathon_participants(
    hackathon_id: int,
    team_status: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie),
):
    hackathon = await get_hack_by_id(session, hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this hackathon"
        )
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
    "/analytics",
    response_model=AnalyticsResponse,
    summary="Получить аналитику хакатона",
    description="Возвращает статистику по хакатону: количество команд, участников, распределение по ролям и т.д.",
    responses={
        200: {"description": "Аналитика успешно получена"},
        403: {"model": ErrorResponse, "description": "Нет прав доступа к хакатону"},
        404: {"model": ErrorResponse, "description": "Хакатон не найден"},
    },
)
async def get_hackathon_analytics(
    hackathon_id: int,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie),
):
    hackathon = await get_hack_by_id(session, hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this hackathon"
        )
    teams_count = await count_teams_for_hack(session, hackathon_id)
    participants_count_result = await session.execute(
        select(TeamMemberModel)
        .join(TeamModel, TeamMemberModel.team_id == TeamModel.id)
        .where(and_(TeamModel.hackathon_id == hackathon_id, TeamMemberModel.user_id.is_not(None)))
    )
    participants_count = len(participants_count_result.scalars().all())
    incomplete_teams_result = await session.execute(
        select(TeamModel).where(
            and_(TeamModel.hackathon_id == hackathon_id, TeamModel.is_completed == False)
        )
    )
    incomplete_teams = len(incomplete_teams_result.scalars().all())
    roles_result = await session.execute(
        select(TeamMemberModel.role, UserModel.name)
        .join(UserModel, TeamMemberModel.user_id == UserModel.id)
        .join(TeamModel, TeamMemberModel.team_id == TeamModel.id)
        .where(and_(TeamModel.hackathon_id == hackathon_id, TeamMemberModel.user_id.is_not(None)))
    )
    role_distribution = {}
    for role, name in roles_result.all():
        role_name = role.value if hasattr(role, "value") else str(role)
        role_distribution[role_name] = role_distribution.get(role_name, 0) + 1
    today = date.today()
    registration_status = "open" if hackathon.start_date > today else "closed"
    days_until_start = (hackathon.start_date - today).days if hackathon.start_date > today else 0
    team_completion_rate = 0
    if teams_count > 0:
        completed_teams = teams_count - incomplete_teams
        team_completion_rate = round((completed_teams / teams_count) * 100, 2)
    average_team_size = 0
    if teams_count > 0:
        average_team_size = round(participants_count / teams_count, 2)
    analytics = AnalyticsResponse(
        hackathon_id=hackathon_id,
        hackathon_name=hackathon.name,
        total_teams=teams_count,
        total_participants=participants_count,
        incomplete_teams=incomplete_teams,
        team_completion_rate=team_completion_rate,
        max_teams=hackathon.max_teams,
        team_size_range={"min": hackathon.min_team_size, "max": hackathon.max_team_size},
        role_distribution=role_distribution,
        remaining_slots=max(0, hackathon.max_teams - teams_count),
        registration_status=registration_status,
        days_until_start=days_until_start,
        average_team_size=average_team_size,
    )
    return analytics


@router.get(
    "/export/csv",
    summary="Экспортировать команды в CSV (скачать файл)",
    description="Скачивает CSV файл с данными о командах и участниках хакатона",
    responses={
        200: {"content": {"text/csv": {}}, "description": "CSV файл успешно сгенерирован"},
        403: {"model": ErrorResponse, "description": "Нет прав доступа к хакатону"},
        404: {"model": ErrorResponse, "description": "Хакатон не найден"},
    },
)
async def export_teams_csv_download(
    hackathon_id: int,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie),
):
    hackathon = await get_hack_by_id(session, hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this hackathon"
        )
    result = await session.execute(
        select(TeamModel, TeamMemberModel, UserModel)
        .join(TeamMemberModel, TeamModel.id == TeamMemberModel.team_id)
        .join(UserModel, TeamMemberModel.user_id == UserModel.id)
        .where(TeamModel.hackathon_id == hackathon_id)
        .where(TeamMemberModel.user_id.is_not(None))
        .order_by(TeamModel.id, UserModel.name)
    )
    rows = result.all()
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    ) as tmp_file:
        writer = csv.writer(tmp_file)
        writer.writerow(
            [
                "ID команды",
                "Название команды",
                "Завершена",
                "ID участника",
                "Имя участника",
                "Роль",
                "Одобрен",
                "ID хакатона",
                "Название хакатона",
            ]
        )
        for team, member, user in rows:
            writer.writerow(
                [
                    team.id,
                    team.name,
                    "Да" if team.is_completed else "Нет",
                    user.id,
                    user.name,
                    member.role.value if hasattr(member.role, "value") else str(member.role),
                    "Да" if member.approved else "Нет",
                    hackathon.id,
                    hackathon.name,
                ]
            )
    filename = f"teams_hackathon_{hackathon_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return FileResponse(tmp_file.name, media_type="text/csv", filename=filename)


@router.post(
    "/teams/{team_id}/approve",
    response_model=TeamApproveResponse,
    summary="Одобрить или отклонить команду",
    description="Изменяет статус одобрения всех участников команды",
    responses={
        200: {"description": "Статус команды успешно изменен"},
        400: {"model": ErrorResponse, "description": "Команда не принадлежит хакатону"},
        403: {"model": ErrorResponse, "description": "Нет прав доступа к хакатону"},
        404: {"model": ErrorResponse, "description": "Хакатон или команда не найдены"},
    },
)
async def approve_team(
    hackathon_id: int,
    team_id: int,
    approve: bool = True,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie),
):
    hackathon = await get_hack_by_id(session, hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this hackathon"
        )
    team = await get_team_by_id(session, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    if team.hackathon_id != hackathon_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Team does not belong to this hackathon"
        )
    members = await get_team_members_by_team_id(session, team_id)
    for member in members:
        member.approved = approve
        session.add(member)
    if approve:
        team.is_completed = True
        session.add(team)
    await session.commit()
    response_message = "approved" if approve else "rejected"
    approved_members = sum(1 for member in members if member.approved)
    response = TeamApproveResponse(
        team_id=team_id,
        approved=approve,
        message=f"Team {team.name} has been {response_message} successfully",
        team_name=team.name,
        total_members=len(members),
        approved_members=approved_members,
    )
    return response


@router.post(
    "/participants/{user_id}/assign",
    response_model=AssignParticipantResponse,
    summary="Вручную распределить участника в команду",
    description="Добавляет участника в команду с указанной ролью",
    responses={
        200: {"description": "Участник успешно распределен"},
        400: {
            "model": ErrorResponse,
            "description": "Некорректные данные: пользователь уже в команде, команда заполнена, неверная роль",
        },
        403: {"model": ErrorResponse, "description": "Нет прав доступа к хакатону"},
        404: {
            "model": ErrorResponse,
            "description": "Хакатон, команда или пользователь не найдены",
        },
    },
)
async def assign_participant_to_team(
    hackathon_id: int,
    user_id: int,
    team_id: int,
    role: str,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer_cookie),
):
    hackathon = await get_hack_by_id(session, hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this hackathon"
        )
    user_result = await session.execute(select(UserModel).where(UserModel.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    team = await get_team_by_id(session, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    if team.hackathon_id != hackathon_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Team does not belong to this hackathon"
        )
    existing_member_result = await session.execute(
        select(TeamMemberModel)
        .join(TeamModel, TeamMemberModel.team_id == TeamModel.id)
        .where(and_(TeamMemberModel.user_id == user_id, TeamModel.hackathon_id == hackathon_id))
    )
    existing_member = existing_member_result.scalar_one_or_none()
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already in a team for this hackathon",
        )
    team_members = await get_team_members_by_team_id(session, team_id)
    real_members_count = sum(1 for member in team_members if member.user_id is not None)
    if real_members_count >= hackathon.max_team_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team already has maximum number of members ({hackathon.max_team_size})",
        )
    try:
        role_enum = RoleType(role.lower())
    except ValueError:
        valid_roles = [role.value for role in RoleType]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{role}'. Valid roles are: {', '.join(valid_roles)}",
        )
    new_member = TeamMemberModel(team_id=team_id, user_id=user_id, role=role_enum, approved=True)
    session.add(new_member)
    if real_members_count + 1 >= hackathon.min_team_size:
        team.is_completed = True
        session.add(team)
    await session.commit()
    response = AssignParticipantResponse(
        success=True,
        message=f"User '{user.name}' has been assigned to team '{team.name}' as {role}",
        team_id=team_id,
        team_name=team.name,
        user_id=user_id,
        user_name=user.name,
        role=role,
        team_completed=team.is_completed,
        team_size_before=real_members_count,
        team_size_after=real_members_count + 1,
    )
    return response
