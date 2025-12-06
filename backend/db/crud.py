from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    HackathonModel,
    ProfileModel,
    ProfileSkillModel,
    SkillModel,
    TeamMemberModel,
    TeamModel,
    UserModel,
)


async def get_hacks(session: AsyncSession, offset: int = 0, limit: int | None = None):
    q = select(HackathonModel).offset(offset)
    if limit is not None:
        q = q.limit(limit)
    result = await session.execute(q)
    return result.scalars().all()


async def count_hacks(session: AsyncSession) -> int:
    result = await session.execute(select(func.count()).select_from(HackathonModel))
    return int(result.scalar_one())


async def get_upcoming_hacks(session: AsyncSession):
    result = await session.execute(
        select(HackathonModel).where(HackathonModel.start_date > func.now())
    )
    return result.scalars().all()


async def get_hack_by_id(session: AsyncSession, hack_id: int):
    result = await session.execute(select(HackathonModel).where(HackathonModel.id == hack_id))
    return result.scalars().first()


async def count_teams_for_hack(session: AsyncSession, hack_id: int) -> int:
    result = await session.execute(
        select(func.count()).select_from(TeamModel).where(TeamModel.hackathon_id == hack_id)
    )
    return int(result.scalar_one())


async def get_users_by_ids(session: AsyncSession, ids: list[int]) -> list[UserModel]:
    if not ids:
        return []

    result = await session.execute(select(UserModel).where(UserModel.id.in_(ids)))
    return result.scalars().all()


async def create_team_with_members(
    session: AsyncSession,
    name: str,
    hack_id: int,
    members: list[dict],
    is_completed: bool,
) -> tuple[TeamModel, list[TeamMemberModel]]:
    """members: список словарей вида {'user_id': int, 'role': RoleType, 'approved': bool}"""
    team = TeamModel(name=name, is_completed=is_completed, hackathon_id=hack_id)
    session.add(team)
    await session.flush()

    team_members = []
    for member in members:
        tm = TeamMemberModel(
            team_id=team.id,
            user_id=member["user_id"],
            role=member["role"],
            approved=member["approved"],
        )
        session.add(tm)
        team_members.append(tm)
    await session.commit()
    return team, team_members


async def get_team_members_by_team_id(session: AsyncSession, team_id: int) -> list[TeamMemberModel]:
    result = await session.execute(
        select(TeamMemberModel).where(TeamMemberModel.team_id == team_id)
    )
    return result.scalars().all()


async def get_team_by_id(session: AsyncSession, team_id: int):
    result = await session.execute(select(TeamModel).where(TeamModel.id == team_id))
    return result.scalars().first()


async def update_team_members(session: AsyncSession, team_id: int, member_ids: list[int]):
    await session.execute(delete(TeamMemberModel).where(TeamMemberModel.team_id == team_id))
    for uid in member_ids:
        session.add(TeamMemberModel(team_id=team_id, user_id=uid))
    await session.commit()


async def get_user_by_id(session: AsyncSession, user_id: int) -> UserModel:
    result = await session.execute(select(UserModel).where(UserModel.id == user_id))
    return result.scalars().first()


async def get_user_by_telegram(session: AsyncSession, tg_id: int) -> UserModel:
    result = await session.execute(select(UserModel).where(UserModel.telegram_id == tg_id))
    return result.scalars().first()


async def create_user_by_telegram(
    session: AsyncSession,
    tg_id: int,
    first_name: str | None,
    last_name: str | None,
    username: str | None,
    photo_url: str | None,
) -> UserModel:
    name = username or " ".join(filter(None, (first_name, last_name))) or ""
    user = UserModel(telegram_id=tg_id, name=name, avatar_url=photo_url or "")
    session.add(user)
    await session.flush()
    await session.refresh(user)
    await session.commit()
    return user


async def update_user_by_telegram(
    session: AsyncSession,
    user: UserModel,
    first_name: str | None,
    last_name: str | None,
    username: str | None,
    photo_url: str | None,
) -> UserModel:
    new_name = username or " ".join(filter(None, (first_name, last_name))) or ""
    new_avatar = photo_url or ""
    changed = False

    if user.name != new_name:
        user.name = new_name
        changed = True
    if user.avatar_url != new_avatar:
        user.avatar_url = new_avatar
        changed = True

    if changed:
        session.add(user)
        await session.flush()
        await session.refresh(user)
        await session.commit()

    return user


async def get_or_create_user_by_telegram(
    session: AsyncSession,
    tg_id: int,
    first_name: str | None,
    last_name: str | None,
    username: str | None,
    photo_url: str | None,
) -> UserModel:
    user = await get_user_by_telegram(session, tg_id)
    if not user:
        user = await create_user_by_telegram(
            session, tg_id, first_name, last_name, username, photo_url
        )
        await create_profile(session, user.id)
        return user

    return await update_user_by_telegram(session, user, first_name, last_name, username, photo_url)


async def get_profile_by_user_id(session: AsyncSession, user_id: int) -> ProfileModel | None:
    result = await session.execute(select(ProfileModel).where(ProfileModel.user_id == user_id))
    return result.scalars().first()


async def create_profile(
    session: AsyncSession, user_id: int, about: str | None = ""
) -> ProfileModel:
    profile = ProfileModel(user_id=user_id, about=about or "")
    session.add(profile)
    await session.flush()
    await session.refresh(profile)
    await session.commit()
    return profile


async def update_profile_about(
    session: AsyncSession, profile: ProfileModel, about: str
) -> ProfileModel:
    profile.about = about or ""
    session.add(profile)
    await session.flush()
    await session.refresh(profile)
    await session.commit()
    return profile


async def set_profile_skills(session: AsyncSession, profile_id: int, skill_ids: list[int]) -> None:
    existing_q = await session.execute(
        select(ProfileSkillModel.skill_id).where(ProfileSkillModel.profile_id == profile_id)
    )
    existing = set(existing_q.scalars().all())
    new = set(skill_ids)

    to_remove = existing - new
    if to_remove:
        await session.execute(
            delete(ProfileSkillModel).where(
                ProfileSkillModel.profile_id == profile_id,
                ProfileSkillModel.skill_id.in_(to_remove),
            )
        )

    to_add = new - existing
    for sid in to_add:
        session.add(ProfileSkillModel(profile_id=profile_id, skill_id=sid))

    await session.commit()


async def get_profile_skill_ids(session: AsyncSession, profile_id: int) -> list[int]:
    result = await session.execute(
        select(ProfileSkillModel.skill_id).where(ProfileSkillModel.profile_id == profile_id)
    )
    return result.scalars().all()


async def get_skills(session: AsyncSession):
    result = await session.execute(select(SkillModel))
    return result.scalars().all()


async def get_skill_by_id(session: AsyncSession, skill_id: int):
    result = await session.execute(select(SkillModel).where(SkillModel.id == skill_id))
    return result.scalars().first()


async def get_skills_by_ids(session: AsyncSession, ids: list[int]) -> list[SkillModel]:
    if not ids:
        return []
    result = await session.execute(select(SkillModel).where(SkillModel.id.in_(ids)))
    return result.scalars().all()


async def get_teams_with_empty_members(session: AsyncSession, hackathon_id: int | None = None):
    q = (
        select(TeamModel, TeamMemberModel)
        .join(TeamMemberModel, TeamModel.id == TeamMemberModel.team_id)
        .where(
            (TeamMemberModel.user_id is None) | (TeamMemberModel.user_id == 0)
        )  # не уверен там нан или 0
    )
    q = q.where(TeamModel.hackathon_id == hackathon_id)
    result = await session.execute(q)
    rows = result.all()
    teams = {}
    for team, member in rows:
        if team.id not in teams:
            teams[team.id] = {"team": team, "members": []}
        teams[team.id]["members"].append(member)
    return list(teams.values())
