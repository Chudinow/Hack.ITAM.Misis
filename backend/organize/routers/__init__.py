# routers/__init__.py
from .organizer_auth import router as organizer_auth_router
from .organizer_hackathons import router as organizer_hackathons_router
from .organizer_teams import router as organizer_teams_router

__all__ = [
    "organizer_auth_router",
    "organizer_hackathons_router", 
    "organizer_teams_router"
]