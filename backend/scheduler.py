import os
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.future import select

from backend.config import settings
from backend.database import AsyncSessionLocal
from backend.models import Video, PlatformPost, JobRun
from backend.services.gemini_service import gemini_service
from backend.services.tts_service import tts_service
from backend.services.video_engine import video_engine
from backend.services.social.facebook import facebook_publisher

logger = logging.getLogger("scheduler")

scheduler = AsyncIOScheduler()

async def run_full_pipeline(
    topic: Optional[str] = None,
    niche: Optional[str] = None,
    voice: Optional[str] = None,
    auto_publish: Optional[bool] = None,
    job_type: str = "MANUAL_TRIGGER"
) -> Video:
    """
    Executes the end-to-end autonomous video creation & publication pipeline:
    1. Gemini: Generates high-retention structured script & prompts
    2. Edge-TTS: Generates neural voiceover audio & duration
    3. Gemini/Imagen: Renders 9:16 vertical scene visuals
    4. Bundled FFmpeg: Compiles 1080x1920 video with Ken-Burns motion
    5. Local Storage & SQLite DB: Stores and indexes all media
    6. Facebook: Auto-posts to Page (if enabled)
    """
    video_uuid = str(uuid.uuid4())
    niche = niche or settings.DEFAULT_NICHE
    voice = voice or settings.DEFAULT_VOICE
    auto_publish = auto_publish if auto_publish is not None else settings.AUTO_PUBLISH_FACEBOOK

    async with AsyncSessionLocal() as db:
        # Create initial JobRun log
        job = JobRun(job_type=job_type, status="RUNNING", started_at=datetime.utcnow(), logs="Starting pipeline...")
        db.add(job)
        await db.commit()
        await db.refresh(job)

        # Create placeholder Video record
        video = Video(
            uuid=video_uuid,
            title="Generating Title...",
            topic=topic or f"Daily Auto-Curation ({niche})",
            niche=niche,
            status="GENERATING",
            created_at=datetime.utcnow()
        )
        db.add(video)
        await db.commit()
        await db.refresh(video)

        job.video_id = video.id
        await db.commit()

        try:
            logger.info(f"[{video_uuid}] Step 1: Generating script with Gemini for niche '{niche}'...")
            job.logs += f"\n[{datetime.utcnow().strftime('%H:%M:%S')}] Generating viral script with Gemini..."
            await db.commit()

            script_data = await gemini_service.generate_reel_script(niche=niche, topic=topic)
            title = script_data.get("title", f"Reel #{video_uuid[:6]}")
            hook = script_data.get("hook", "")
            scenes = script_data.get("scenes", [])
            cta = script_data.get("call_to_action", "")
            caption = script_data.get("caption", title)

            # Combine full spoken text: Hook -> Scenes -> CTA
            narration_parts = [hook] if hook else []
            for sc in scenes:
                narration_parts.append(sc.get("narration", ""))
            if cta:
                narration_parts.append(cta)
            full_narration = " ".join([p for p in narration_parts if p.strip()])

            # Update DB with script details
            video.title = title
            video.hook = hook
            video.narration_text = full_narration
            video.caption = caption
            video.script_data = script_data
            await db.commit()

            # Step 2: Voiceover generation
            logger.info(f"[{video_uuid}] Step 2: Synthesizing voiceover with Edge-TTS...")
            job.logs += f"\n[{datetime.utcnow().strftime('%H:%M:%S')}] Synthesizing neural voiceover ({voice})..."
            await db.commit()

            audio_file_path = str(settings.audio_path / f"{video_uuid}.mp3")
            tts_result = await tts_service.generate_audio_and_subtitles(
                text=full_narration,
                output_audio_path=audio_file_path,
                voice=voice
            )
            audio_duration = tts_result["duration"]
            video.audio_path = audio_file_path
            await db.commit()

            # Step 3: Scene visuals generation
            logger.info(f"[{video_uuid}] Step 3: Generating scene visuals...")
            job.logs += f"\n[{datetime.utcnow().strftime('%H:%M:%S')}] Generating {len(scenes)} vertical scene visuals..."
            await db.commit()

            scene_image_paths = []
            for sc in scenes:
                sc_num = sc.get("scene_number", 1)
                img_path = str(settings.images_path / f"{video_uuid}_scene_{sc_num}.jpg")
                prompt = sc.get("visual_prompt", title)
                saved_img = await gemini_service.generate_scene_image(
                    prompt=prompt,
                    output_path=img_path,
                    scene_num=sc_num,
                    title=title
                )
                scene_image_paths.append(saved_img)

            # Step 4: Render Video with bundled FFmpeg
            logger.info(f"[{video_uuid}] Step 4: Compiling 1080x1920 MP4 video...")
            job.logs += f"\n[{datetime.utcnow().strftime('%H:%M:%S')}] Rendering video with Ken-Burns motion & H.264 encoding..."
            await db.commit()

            render_res = await video_engine.render_reel(
                video_uuid=video_uuid,
                image_paths=scene_image_paths,
                audio_path=audio_file_path,
                duration=audio_duration,
                title=title
            )

            # Update video record
            video.status = "READY"
            video.video_path = render_res["video_path"]
            video.thumbnail_path = render_res["thumbnail_path"]
            video.duration_seconds = render_res["duration_seconds"]
            video.file_size_bytes = render_res["file_size_bytes"]
            video.resolution = render_res["resolution"]
            await db.commit()

            # Step 5: Auto-Publishing to Facebook if configured
            if auto_publish:
                logger.info(f"[{video_uuid}] Step 5: Auto-publishing video to Facebook...")
                job.logs += f"\n[{datetime.utcnow().strftime('%H:%M:%S')}] Auto-publishing to Facebook Page..."
                await db.commit()

                fb_res = await facebook_publisher.publish_video(
                    video_path=video.video_path,
                    title=video.title,
                    caption=video.caption,
                    thumbnail_path=video.thumbnail_path
                )

                post_status = "SUCCESS" if fb_res["success"] else "FAILED"
                post_record = PlatformPost(
                    video_id=video.id,
                    platform="FACEBOOK",
                    status=post_status,
                    platform_post_id=fb_res.get("post_id"),
                    platform_url=fb_res.get("post_url"),
                    error_message=fb_res.get("error"),
                    posted_at=datetime.utcnow() if fb_res["success"] else None
                )
                db.add(post_record)

                if fb_res["success"]:
                    video.status = "POSTED"
                    job.logs += f"\n[{datetime.utcnow().strftime('%H:%M:%S')}] Published to Facebook! Post ID: {fb_res.get('post_id')}"
                else:
                    job.logs += f"\n[{datetime.utcnow().strftime('%H:%M:%S')}] Facebook publish failed: {fb_res.get('error')}"
                await db.commit()

            # Mark job complete
            job.status = "SUCCESS"
            job.completed_at = datetime.utcnow()
            job.logs += f"\n[{datetime.utcnow().strftime('%H:%M:%S')}] Pipeline completed successfully!"
            await db.commit()
            await db.refresh(video)

            logger.info(f"[{video_uuid}] Pipeline successfully finished.")
            return video

        except Exception as e:
            logger.error(f"[{video_uuid}] Pipeline failed with error: {e}", exc_info=True)
            video.status = "FAILED"
            video.error_message = str(e)
            job.status = "FAILED"
            job.completed_at = datetime.utcnow()
            job.logs += f"\n[{datetime.utcnow().strftime('%H:%M:%S')}] FAILED: {str(e)}"
            await db.commit()
            raise e

async def scheduled_daily_runner():
    logger.info("Executing scheduled daily automated video creation...")
    try:
        await run_full_pipeline(
            topic=None,
            niche=settings.DEFAULT_NICHE,
            voice=settings.DEFAULT_VOICE,
            auto_publish=settings.AUTO_PUBLISH_FACEBOOK,
            job_type="DAILY_AUTOMATION"
        )
    except Exception as e:
        logger.error(f"Scheduled daily run error: {e}")

def start_scheduler():
    """Initializes APScheduler background schedule"""
    if not scheduler.running:
        trigger = CronTrigger(
            hour=settings.DAILY_SCHEDULE_HOUR,
            minute=settings.DAILY_SCHEDULE_MINUTE
        )
        scheduler.add_job(
            scheduled_daily_runner,
            trigger=trigger,
            id="daily_video_job",
            replace_existing=True
        )
        scheduler.start()
        logger.info(f"Scheduler active: Runs daily at {settings.DAILY_SCHEDULE_HOUR:02d}:{settings.DAILY_SCHEDULE_MINUTE:02d}")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
