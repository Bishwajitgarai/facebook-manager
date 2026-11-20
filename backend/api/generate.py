import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import List, Dict, Any

from backend.schemas import GenerateVideoRequest, ScriptData
from backend.services.gemini_service import gemini_service
from backend.services.tts_service import tts_service
from backend.scheduler import run_full_pipeline

router = APIRouter(prefix="/generate", tags=["Generation"])

@router.post("")
async def generate_video_endpoint(
    payload: GenerateVideoRequest,
    background_tasks: BackgroundTasks
):
    """
    Triggers end-to-end video generation pipeline in the background.
    """
    # Run the pipeline as a background task
    async def task_wrapper():
        try:
            await run_full_pipeline(
                topic=payload.topic,
                niche=payload.niche,
                voice=payload.voice,
                auto_publish=payload.auto_publish_facebook,
                job_type="MANUAL_TRIGGER"
            )
        except Exception as e:
            pass

    asyncio.create_task(task_wrapper())

    return {
        "status": "QUEUED",
        "message": "Video generation pipeline started! You can track live progress in the Videos feed.",
        "topic": payload.topic or "Auto Curation",
        "niche": payload.niche
    }

@router.post("/preview-script", response_model=Dict[str, Any])
async def preview_script(payload: GenerateVideoRequest):
    """Generates and previews the Gemini script and scene visuals without rendering video"""
    try:
        script = await gemini_service.generate_reel_script(
            niche=payload.niche or "Tech & AI Horizons",
            topic=payload.topic
        )
        return script
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voices")
async def list_voices():
    """Lists available high-quality neural voices"""
    return tts_service.get_available_voices()
