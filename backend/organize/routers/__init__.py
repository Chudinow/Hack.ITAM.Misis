from .organizer_auth import router as organizer_auth_router
from .organizer_hackathons import router as organizer_hackathons_router
from .organizer_teams import router as organizer_teams_router
from .public import router as public_router

__all__ = [
    "organizer_auth_router",
    "organizer_hackathons_router",
    "organizer_teams_router",
    "public_router"
]