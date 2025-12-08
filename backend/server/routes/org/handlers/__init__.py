from .auth import router as organizer_auth_router
from .hackathons import router as organizer_hackathons_router
from .public import router as public_router
from .teams import router as organizer_teams_router

__all__ = [
    "organizer_auth_router",
    "organizer_hackathons_router",
    "organizer_teams_router",
    "public_router",
]
