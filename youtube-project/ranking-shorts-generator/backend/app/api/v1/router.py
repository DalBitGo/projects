from fastapi import APIRouter
from app.api.v1.endpoints import search, projects, videos, settings

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
