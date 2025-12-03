"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import jobs
from app.config import settings
from app.database import close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="StoreBridge API",
    description="Automated product import system from Domeggook to Naver Smart Store",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs.router, prefix="/v1")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "StoreBridge API",
        "version": "0.1.0",
        "status": "healthy",
        "environment": settings.environment,
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    # TODO: Check database, Redis, etc.
    return {
        "status": "healthy",
        "components": {
            "database": "healthy",
            "redis": "healthy",
            "celery": "healthy",
        },
    }
