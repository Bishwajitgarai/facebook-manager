from fastapi import APIRouter, HTTPException
from backend.config import settings
from backend.scheduler import scheduler, run_full_pipeline
from backend.schemas import SchedulerConfigRequest
from apscheduler.triggers.cron import CronTrigger
import asyncio

router = APIRouter(prefix="/schedule", tags=["Schedule"])

@router.get("")
async def get_schedule_status():
    """Returns current automation schedule configuration"""
    job = scheduler.get_job("daily_video_job")
    next_run = str(job.next_run_time) if job and job.next_run_time else None
    return {
        "hour": settings.DAILY_SCHEDULE_HOUR,
        "minute": settings.DAILY_SCHEDULE_MINUTE,
        "auto_publish": settings.AUTO_PUBLISH_FACEBOOK,
        "niche": settings.DEFAULT_NICHE,
        "is_active": scheduler.running,
        "next_run_time": next_run
    }

@router.post("")
async def update_schedule(config: SchedulerConfigRequest):
    """Updates daily schedule execution time and auto-publish setting"""
    settings.DAILY_SCHEDULE_HOUR = config.hour
    settings.DAILY_SCHEDULE_MINUTE = config.minute
    settings.AUTO_PUBLISH_FACEBOOK = config.auto_publish
    settings.DEFAULT_NICHE = config.niche

    trigger = CronTrigger(hour=config.hour, minute=config.minute)
    scheduler.reschedule_job("daily_video_job", trigger=trigger)

    job = scheduler.get_job("daily_video_job")
    return {
        "status": "UPDATED",
        "message": f"Daily schedule updated to {config.hour:02d}:{config.minute:02d}",
        "next_run_time": str(job.next_run_time) if job and job.next_run_time else None
    }

@router.post("/run-now")
async def trigger_now():
    """Immediately triggers the daily automation pipeline without waiting for schedule"""
    asyncio.create_task(run_full_pipeline(job_type="MANUAL_DAILY_TRIGGER"))
    return {"status": "TRIGGERED", "message": "Daily automation run started in background."}
