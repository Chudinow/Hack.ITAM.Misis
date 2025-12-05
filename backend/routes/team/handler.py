from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from routes.team.schema import TeamCreate, TeamResponse, TeamWithMembersResponse, TeamUpdate

router = APIRouter(prefix="/api/team", tags=["teams"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_team(payload: TeamCreate, db: AsyncSession = Depends(get_session)) -> TeamResponse: ...


@router.put("/{team_id}")
def update_team(
    team_id: int, payload: TeamUpdate, db: AsyncSession = Depends(get_session)
) -> TeamResponse: ...


# капитаном команды будет тот человек, который первый в списке участников, т.е. тот, кто ее регистрировал
# менять состав может только капитан


@router.get("/{team_id}")
def get_team_by_id(
    team_id: int, db: AsyncSession = Depends(get_session)
) -> TeamWithMembersResponse: ...
