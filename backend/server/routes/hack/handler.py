from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from db import crud, get_session

from .schema import HackListSchema, HackSchema, MetaSchema

router = APIRouter(prefix="/api/hack", tags=["hackathon"])


@router.get("/{hack_id}")
async def get_hack_by_id(hack_id: int, session: AsyncSession = Depends(get_session)) -> HackSchema:
    hack = await crud.get_hack_by_id(session, hack_id)
    if hack is None:
        raise HTTPException(HTTP_404_NOT_FOUND, "Хакатона с таким id не существует.")

    return HackSchema(
        id=hack.id,
        name=hack.name,
        description=hack.description,
        photo_url=hack.photo_url,
        start_date=hack.start_date,
        end_date=hack.end_date,
        tags=hack.tags,
    )


@router.get("/all")
async def get_all_hacks(
    page: int = Query(1, ge=1),  # 1 <= page
    per_page: int = Query(20, ge=1, le=50),  # 1 <= per_page <= 50
    session: AsyncSession = Depends(get_session),
) -> HackListSchema:
    offset = (page - 1) * per_page
    hacks = await crud.get_hacks(session, offset=offset, limit=per_page)
    total = await crud.count_hacks(session)

    items = [
        HackSchema(
            id=hack.id,
            name=hack.name,
            description=hack.description,
            photo_url=hack.photo_url,
            start_date=hack.start_date,
            end_date=hack.end_date,
            tags=hack.tags,
        )
        for hack in hacks
    ]

    total_pages = ceil(total / per_page) if per_page else 0
    if total_pages and page > total_pages:
        return HackListSchema(
            hacks=[],
            meta=MetaSchema(
                total=total,
                page=page,
                per_page=per_page,
                total_pages=total_pages,
                next_page=None,
            ),
        )

    return HackListSchema(
        hacks=items,
        meta=MetaSchema(
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        ),
    )


@router.get("/upcoming")
async def get_upcoming_hacks(session: AsyncSession = Depends(get_session)) -> HackListSchema:
    hacks = await crud.get_upcoming_hacks(session)
    return HackListSchema(
        hacks=[
            HackSchema(
                id=hack.id,
                name=hack.name,
                description=hack.description,
                photo_url=hack.photo_url,
                start_date=hack.start_date,
                end_date=hack.end_date,
                tags=hack.tags,
            )
            for hack in hacks
        ]
    )
