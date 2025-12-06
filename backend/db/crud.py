from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import HackathonModel


async def get_hacks(session: AsyncSession):
    result = await session.execute(select(HackathonModel))
    return result.scalars().all()


async def get_hack_by_id(session: AsyncSession, hack_id: int):
    result = await session.execute(select(HackathonModel).where(HackathonModel.id == hack_id))
    return result.scalars().first()
