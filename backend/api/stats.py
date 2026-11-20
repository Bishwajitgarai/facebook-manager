import os
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from backend.config import settings
from backend.database import get_db
from backend.models import Video, JobRun
from backend.scheduler import scheduler
from backend.services.social.facebook import facebook_publisher

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Computes overall library, platform, and storage stats"""
    total_videos = await db.scalar(select(func.count(Video.id))) or 0
    ready_videos = await db.scalar(select(func.count(Video.id)).where(Video.status == "READY")) or 0
    posted_videos = await db.scalar(select(func.count(Video.id)).where(Video.status == "POSTED")) or 0

    # Calculate total local video storage used
    storage_bytes = 0
    storage_dir = settings.storage_path
    if storage_dir.exists():
        for root, _, files in os.walk(storage_dir):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    storage_bytes += os.path.getsize(fp)
                except Exception:
                    pass

    storage_mb = round(storage_bytes / (1024 * 1024), 2)

    # Scheduler info
    job = scheduler.get_job("daily_video_job")
    next_run = str(job.next_run_time) if job and job.next_run_time else None

    # Last job run
    last_job = await db.execute(select(JobRun).order_by(JobRun.started_at.desc()).limit(1))
    last_job_row = last_job.scalars().first()
    last_status = last_job_row.status if last_job_row else "NONE"

    # Connectivity checks
    fb_configured = bool(settings.FACEBOOK_PAGE_ID and settings.FACEBOOK_PAGE_ACCESS_TOKEN)
    gemini_configured = bool(settings.GEMINI_API_KEY)

    return {
        "total_videos": total_videos,
        "ready_videos": ready_videos,
        "posted_videos": posted_videos,
        "total_storage_mb": storage_mb,
        "next_scheduled_run": next_run,
        "last_run_status": last_status,
        "facebook_connected": fb_configured,
        "gemini_connected": gemini_configured,
        "default_niche": settings.DEFAULT_NICHE,
        "storage_path": str(settings.storage_path.resolve())
    }
