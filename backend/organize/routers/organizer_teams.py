# routers/organizer_teams.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, not_
from typing import List, Optional
import csv
from io import StringIO
from datetime import datetime
from fastapi.responses import StreamingResponse

from db import get_session  
from db.models import (
    HackathonModel, 
    TeamModel, 
    TeamMemberModel, 
    UserModel,
    ProfileModel,
    ProfileSkillModel,
    SkillModel,
    OrganizerModel, 
    RoleType  
)
from schemas.hackathon import TeamResponse, ParticipantResponse
from dependencies import get_current_organizer  
#CRUD функции
try:
    from db.crud import (
        get_hack_by_id,
        get_team_by_id,
        get_team_members_by_team_id,
        get_users_by_ids,
        get_profile_by_user_id,
        get_profile_skill_ids,
        get_skills_by_ids,
        count_teams_for_hack
    )
except ImportError:
    # Если CRUD функций нет, определим их здесь
    async def get_hack_by_id(session: AsyncSession, hack_id: int):
        result = await session.execute(
            select(HackathonModel).where(HackathonModel.id == hack_id)
        )
        return result.scalars().first()
    
    async def get_team_by_id(session: AsyncSession, team_id: int):
        result = await session.execute(
            select(TeamModel).where(TeamModel.id == team_id)
        )
        return result.scalars().first()
    
    async def get_team_members_by_team_id(session: AsyncSession, team_id: int):
        result = await session.execute(
            select(TeamMemberModel).where(TeamMemberModel.team_id == team_id)
        )
        return result.scalars().all()
    
    async def count_teams_for_hack(session: AsyncSession, hack_id: int):
        result = await session.execute(
            select(TeamModel).where(TeamModel.hackathon_id == hack_id)
        )
        teams = result.scalars().all()
        return len(teams)

router = APIRouter(prefix="/organizer/hackathons/{hackathon_id}", tags=["organizer_teams"])


@router.get("/teams", response_model=List[TeamResponse])
async def get_hackathon_teams(
    hackathon_id: int,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer)  # ✅ Теперь работает
):
    """Получить все команды хакатона с участниками"""
    
    # Проверяем права
    hackathon = await get_hack_by_id(session, hackathon_id)
    
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this hackathon"
        )
    
    # Получаем все команды хакатона
    result = await session.execute(
        select(TeamModel).where(TeamModel.hackathon_id == hackathon_id)
    )
    teams = result.scalars().all()
    
    response_teams = []
    for team in teams:
        # Получаем участников команды
        members = await get_team_members_by_team_id(session, team.id)
        
        # Получаем информацию о пользователях
        member_responses = []
        for member in members:
            user_info = {}
            if member.user_id:
                user_result = await session.execute(
                    select(UserModel).where(UserModel.id == member.user_id)
                )
                user = user_result.scalar_one_or_none()
                if user:
                    user_info = {
                        "user_name": user.name,
                        "user_avatar": user.avatar_url
                    }
            
            member_responses.append({
                "id": member.id,
                "user_id": member.user_id,
                "role": member.role.value if hasattr(member.role, 'value') else str(member.role),
                "approved": member.approved,
                **user_info
            })
        
        response_teams.append({
            "id": team.id,
            "name": team.name,
            "is_completed": team.is_completed,
            "hackathon_id": team.hackathon_id,
            "members": member_responses
        })
    
    return response_teams


@router.get("/participants", response_model=List[ParticipantResponse])
async def get_hackathon_participants(
    hackathon_id: int,
    team_status: Optional[str] = None,  # "with_team", "without_team"
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer)
):
    """Получить всех участников хакатона с фильтрацией"""
    
    # Проверяем права
    hackathon = await get_hack_by_id(session, hackathon_id)
    
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this hackathon"
        )
    
    # Получаем всех участников команд этого хакатона
    result = await session.execute(
        select(TeamMemberModel, UserModel, TeamModel)
        .join(UserModel, TeamMemberModel.user_id == UserModel.id)
        .join(TeamModel, TeamMemberModel.team_id == TeamModel.id)
        .where(TeamModel.hackathon_id == hackathon_id)
        .where(TeamMemberModel.user_id.is_not(None))
    )
    
    rows = result.all()
    
    # Собираем участников с командами
    participants_with_teams = {}
    for member, user, team in rows:
        if user.id not in participants_with_teams:
            participants_with_teams[user.id] = {
                "user": user,
                "team": team,
                "role": member.role
            }
    
    # Получаем профили для скиллов
    participants = []
    for user_id, data in participants_with_teams.items():
        user = data["user"]
        
        # Получаем профиль и скиллы
        profile = await get_profile_by_user_id(session, user.id)
        skills = []
        if profile:
            skill_ids = await get_profile_skill_ids(session, profile.id)
            skill_objs = await get_skills_by_ids(session, skill_ids)
            skills = [skill.name for skill in skill_objs]
        
        # Используем метод from_orm для преобразования
        participant_data = {
            "user_id": user.id,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "has_team": True,
            "team_name": data["team"].name,
            "role": data["role"].value if hasattr(data["role"], 'value') else str(data["role"]),
            "skills": skills
        }
        
        # Создаем объект ParticipantResponse
        participant = ParticipantResponse(**participant_data)
        participants.append(participant)
    
    # Если нужны участники без команд
    if team_status == "without_team" or team_status is None:
        # Получаем ID всех пользователей, которые уже в командах
        user_ids_in_teams = list(participants_with_teams.keys())
        
        # Запрос для пользователей без команд
        query = select(UserModel)
        if user_ids_in_teams:
            query = query.where(UserModel.id.notin_(user_ids_in_teams))
        
        result = await session.execute(query)
        users_without_teams = result.scalars().all()
        
        for user in users_without_teams:
            # Пропускаем если нужен статус with_team
            if team_status == "with_team":
                continue
            
            # Получаем профиль и скиллы
            profile = await get_profile_by_user_id(session, user.id)
            skills = []
            if profile:
                skill_ids = await get_profile_skill_ids(session, profile.id)
                skill_objs = await get_skills_by_ids(session, skill_ids)
                skills = [skill.name for skill in skill_objs]
            
            participant_data = {
                "user_id": user.id,
                "name": user.name,
                "avatar_url": user.avatar_url,
                "has_team": False,
                "team_name": None,
                "role": None,
                "skills": skills
            }
            
            participant = ParticipantResponse(**participant_data)
            participants.append(participant)
    
    # Фильтруем по team_status если указан
    if team_status == "with_team":
        participants = [p for p in participants if p.has_team]
    elif team_status == "without_team":
        participants = [p for p in participants if not p.has_team]
    
    return participants


@router.get("/analytics")
async def get_hackathon_analytics(
    hackathon_id: int,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer)
):
    """Получить аналитику по хакатону"""
    
    # Проверяем права
    hackathon = await get_hack_by_id(session, hackathon_id)
    
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this hackathon"
        )
    
    # Количество команд
    teams_count = await count_teams_for_hack(session, hackathon_id)
    
    # Количество участников с командами
    participants_count_result = await session.execute(
        select(TeamMemberModel)
        .join(TeamModel, TeamMemberModel.team_id == TeamModel.id)
        .where(
            and_(
                TeamModel.hackathon_id == hackathon_id,
                TeamMemberModel.user_id.is_not(None)
            )
        )
    )
    participants_count = len(participants_count_result.scalars().all())
    
    # Команды без участников (или с незаполненными слотами)
    incomplete_teams_result = await session.execute(
        select(TeamModel)
        .where(TeamModel.hackathon_id == hackathon_id)
        .where(TeamModel.is_completed == False)
    )
    incomplete_teams = len(incomplete_teams_result.scalars().all())
    
    # Распределение по ролям
    roles_result = await session.execute(
        select(TeamMemberModel.role, UserModel.name)
        .join(UserModel, TeamMemberModel.user_id == UserModel.id)
        .join(TeamModel, TeamMemberModel.team_id == TeamModel.id)
        .where(
            and_(
                TeamModel.hackathon_id == hackathon_id,
                TeamMemberModel.user_id.is_not(None)
            )
        )
    )
    
    role_distribution = {}
    for role, name in roles_result.all():
        role_name = role.value if hasattr(role, 'value') else str(role)
        role_distribution[role_name] = role_distribution.get(role_name, 0) + 1
    
    # Проверяем даты
    from datetime import date
    today = date.today()
    
    return {
        "hackathon_id": hackathon_id,
        "hackathon_name": hackathon.name,
        "total_teams": teams_count,
        "total_participants": participants_count,
        "incomplete_teams": incomplete_teams,
        "team_completion_rate": (
            round(((teams_count - incomplete_teams) / teams_count * 100), 2)
            if teams_count > 0 else 0
        ),
        "max_teams": hackathon.max_teams,
        "team_size_range": {
            "min": hackathon.min_team_size,
            "max": hackathon.max_team_size
        },
        "role_distribution": role_distribution,
        "remaining_slots": hackathon.max_teams - teams_count,
        "registration_status": "open" if hackathon.start_date > today else "closed",
        "days_until_start": (hackathon.start_date - today).days if hackathon.start_date > today else 0
    }


@router.get("/export/teams")
async def export_teams_csv(
    hackathon_id: int,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer)
):
    """Экспорт команд хакатона в CSV"""
    
    # Проверяем права
    hackathon = await get_hack_by_id(session, hackathon_id)
    
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this hackathon"
        )
    
    # Получаем команды с участниками
    result = await session.execute(
        select(TeamModel, TeamMemberModel, UserModel)
        .join(TeamMemberModel, TeamModel.id == TeamMemberModel.team_id)
        .join(UserModel, TeamMemberModel.user_id == UserModel.id)
        .where(TeamModel.hackathon_id == hackathon_id)
        .where(TeamMemberModel.user_id.is_not(None))
        .order_by(TeamModel.id, UserModel.name)
    )
    
    rows = result.all()
    
    # Создаем CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Заголовки
    writer.writerow([
        "Team ID", "Team Name", "Is Completed", 
        "User ID", "User Name", "Role", "Approved"
    ])
    
    # Данные
    for team, member, user in rows:
        writer.writerow([
            team.id,
            team.name,
            "Yes" if team.is_completed else "No",
            user.id,
            user.name,
            member.role.value if hasattr(member.role, 'value') else str(member.role),
            "Yes" if member.approved else "No"
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=teams_hackathon_{hackathon_id}.csv"
        }
    )


@router.post("/teams/{team_id}/approve")
async def approve_team(
    hackathon_id: int,
    team_id: int,
    approve: bool = True,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer)
):
    """Одобрить/отклонить команду"""
    
    # Проверяем права
    hackathon = await get_hack_by_id(session, hackathon_id)
    
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this hackathon"
        )
    
    # Получаем команду
    team = await get_team_by_id(session, team_id)
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    if team.hackathon_id != hackathon_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team does not belong to this hackathon"
        )
    
    # Обновляем статус участников команды
    members = await get_team_members_by_team_id(session, team_id)
    for member in members:
        member.approved = approve
        session.add(member)
    
    # Помечаем команду как завершенную если одобрена
    if approve:
        team.is_completed = True
    
    await session.commit()
    
    return {
        "team_id": team_id,
        "approved": approve,
        "message": f"Team {'approved' if approve else 'rejected'} successfully"
    }


@router.post("/participants/{user_id}/assign")
async def assign_participant_to_team(
    hackathon_id: int,
    user_id: int,
    team_id: int,
    role: str,
    session: AsyncSession = Depends(get_session),
    current_organizer: OrganizerModel = Depends(get_current_organizer)
):
    """Вручную распределить участника в команду"""
    
    # Проверяем права
    hackathon = await get_hack_by_id(session, hackathon_id)
    
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )
    
    if hackathon.organizer_id != current_organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this hackathon"
        )
    
    # Проверяем пользователя
    user_result = await session.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Проверяем команду
    team = await get_team_by_id(session, team_id)
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    if team.hackathon_id != hackathon_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team does not belong to this hackathon"
        )
    
    # Проверяем, не состоит ли уже пользователь в другой команде этого хакатона
    existing_member_result = await session.execute(
        select(TeamMemberModel)
        .join(TeamModel, TeamMemberModel.team_id == TeamModel.id)
        .where(
            and_(
                TeamMemberModel.user_id == user_id,
                TeamModel.hackathon_id == hackathon_id
            )
        )
    )
    existing_member = existing_member_result.scalar_one_or_none()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already in a team for this hackathon"
        )
    
    # Проверяем размер команды
    team_members = await get_team_members_by_team_id(session, team_id)
    real_members_count = sum(1 for m in team_members if m.user_id is not None)
    
    if real_members_count >= hackathon.max_team_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team already has maximum number of members ({hackathon.max_team_size})"
        )
    
    # Создаем участника команды
    try:
        role_enum = RoleType(role.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {[r.value for r in RoleType]}"
        )
    
    new_member = TeamMemberModel(
        team_id=team_id,
        user_id=user_id,
        role=role_enum,
        approved=True  # Автоматически одобряем при ручном распределении
    )
    
    session.add(new_member)
    
    # Проверяем, заполнена ли теперь команда
    updated_members = await get_team_members_by_team_id(session, team_id)
    real_members_after = sum(1 for m in updated_members if m.user_id is not None)
    
    if real_members_after >= hackathon.min_team_size:
        team.is_completed = True
    
    await session.commit()
    
    return {
        "success": True,
        "message": f"User {user.name} assigned to team {team.name} as {role}",
        "team_id": team_id,
        "user_id": user_id,
        "team_completed": team.is_completed
    }