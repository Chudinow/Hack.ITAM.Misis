from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    HackathonModel,
    TeamModel,
    TeamMemberModel,
    UserModel,
)


async def get_hacks(session: AsyncSession):
    result = await session.execute(select(HackathonModel))
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


async def create_team(session: AsyncSession, name: str, hack_id: int, member_ids: list[int]):
    team = TeamModel(name=name, is_completed=False, hackathon_id=hack_id)
    session.add(team)
    await session.flush()

    for uid in member_ids:
        session.add(TeamMemberModel(team_id=team.id, user_id=uid))
    await session.commit()

    return team


async def get_team_by_id(session: AsyncSession, team_id: int):
    result = await session.execute(select(TeamModel).where(TeamModel.id == team_id))
    return result.scalars().first()


async def update_team_members(session: AsyncSession, team_id: int, member_ids: list[int]):
    await session.execute(delete(TeamMemberModel).where(TeamMemberModel.team_id == team_id))
    for uid in member_ids:
        session.add(TeamMemberModel(team_id=team_id, user_id=uid))
    await session.commit()


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
        return await create_user_by_telegram(
            session, tg_id, first_name, last_name, username, photo_url
        )

    return await update_user_by_telegram(session, user, first_name, last_name, username, photo_url)
