"""FastAPI application."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Safety Inspection Finding Management System",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Easy Safety Inspection API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


# Include API routers
from app.api.v1 import auth, findings, areas, users, notifications  # noqa: E402

app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/v1/auth", tags=["Authentication"])
app.include_router(findings.router, prefix=f"{settings.API_PREFIX}/v1/findings", tags=["Findings"])
app.include_router(areas.router, prefix=f"{settings.API_PREFIX}/v1/areas", tags=["Areas"])
app.include_router(users.router, prefix=f"{settings.API_PREFIX}/v1/admin/users", tags=["Admin"])
app.include_router(notifications.router, prefix=f"{settings.API_PREFIX}/v1/notifications", tags=["Notifications"])
