import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.config import settings
from backend.database import init_db, migrate_from_sqlite_if_needed
from backend.scheduler import start_scheduler, stop_scheduler
from backend.services.redis_service import redis_service
from backend.api import videos, generate, publish, schedule, stats

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("almost_real")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure DB tables exist & migrate from SQLite if running PostgreSQL
    logger.info("Initializing database schema (PostgreSQL / SQLite)...")
    await init_db()
    await migrate_from_sqlite_if_needed()
    
    # Verify Redis connection & sync environment variables to Redis cache
    redis_ok = await redis_service.sync_env_to_redis()
    if redis_ok:
        logger.info("Connected to Redis cache and synced environment variables.")
    else:
        logger.info("Redis offline or unreachable: operating seamlessly via local env / database fallback.")

    logger.info("Starting Daily Video Creation Scheduler...")
    start_scheduler()
    yield
    # Shutdown cleanly
    logger.info("Shutting down Daily Scheduler...")
    stop_scheduler()
    await redis_service.close()

app = FastAPI(
    title="Almost Real AI Studio API",
    description="Autonomous AI Video Engine & Social Sync (Facebook, Instagram, YouTube) with Redis & PostgreSQL",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for Next.js Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Build API v1 Router
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(videos.router)
api_v1_router.include_router(generate.router)
api_v1_router.include_router(publish.router)
api_v1_router.include_router(schedule.router)
api_v1_router.include_router(stats.router)

@api_v1_router.get("/health")
async def health_check():
    redis_status = await redis_service.check_health()
    db_type = "PostgreSQL" if "postgresql" in settings.DATABASE_URL else "SQLite"
    return {
        "status": "healthy",
        "service": "Almost Real AI Engine",
        "version": "1.0.0",
        "database": db_type,
        "redis_connected": redis_status,
        "daily_scheduler": "active"
    }

# Mount both /api/v1 (primary versioned) and /api (convenience legacy)
app.include_router(api_v1_router)

# Also mount legacy /api router pointing to same endpoints
api_legacy_router = APIRouter(prefix="/api")
api_legacy_router.include_router(videos.router)
api_legacy_router.include_router(generate.router)
api_legacy_router.include_router(publish.router)
api_legacy_router.include_router(schedule.router)
api_legacy_router.include_router(stats.router)
api_legacy_router.add_api_route("/health", health_check, methods=["GET"])
app.include_router(api_legacy_router)

# Check if pre-built frontend exists to serve alongside API
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "out"
if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
