from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from db import crud, get_session
from routes.hack.schema import HackListSchema, HackSchema

router = APIRouter()


@router.get("/api/hack/list")
async def get_all_hacks(session: AsyncSession = Depends(get_session)) -> HackListSchema:
    hacks = await crud.get_hacks(session)
    return HackListSchema(
        hacks=[
            HackSchema(
                id=hack.id,
                name=hack.name,
                description=hack.description,
                start_date=hack.start_date,
                end_date=hack.start_date,
                tags=hack.tags,
            )
            for hack in hacks
        ]
    )


@router.get("/api/hack/{id}")
async def get_hack_by_id(id: int, session: AsyncSession = Depends(get_session)) -> HackSchema:
    hack = await crud.get_hack_by_id(session, id)
    if hack is None:
        raise HTTPException(HTTP_404_NOT_FOUND, "Хакатона с таким id не существует.")

    return HackSchema(
        id=hack.id,
        name=hack.name,
        description=hack.description,
        start_date=hack.start_date,
        end_date=hack.end_date,
        tags=hack.tags,
    )
