from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from backend.database import get_db
from backend.models import Video, PlatformPost
from backend.schemas import PublishRequest
from backend.services.social.facebook import facebook_publisher
from backend.services.social.instagram import instagram_publisher
from backend.services.social.youtube import youtube_publisher

router = APIRouter(prefix="/publish", tags=["Publishing"])

@router.get("/facebook/status")
async def check_facebook_status():
    """Verifies Facebook Page ID and Token validity"""
    return await facebook_publisher.verify_connection()

@router.post("/{video_id}")
async def publish_video_endpoint(
    video_id: int,
    payload: PublishRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Manually publishes a stored video to Facebook, Instagram, or YouTube.
    """
    query = select(Video).where(Video.id == video_id)
    result = await db.execute(query)
    video = result.scalars().first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    caption = payload.custom_caption or video.caption or video.title
    results = {}

    for platform in payload.platforms:
        platform_upper = platform.upper()
        if platform_upper == "FACEBOOK":
            fb_res = await facebook_publisher.publish_video(
                video_path=video.video_path,
                title=video.title,
                caption=caption,
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
            results["FACEBOOK"] = fb_res

        elif platform_upper == "INSTAGRAM":
            ig_res = await instagram_publisher.publish_video(
                video_path=video.video_path,
                title=video.title,
                caption=caption,
                thumbnail_path=video.thumbnail_path
            )
            results["INSTAGRAM"] = ig_res

        elif platform_upper == "YOUTUBE":
            yt_res = await youtube_publisher.publish_video(
                video_path=video.video_path,
                title=video.title,
                caption=caption,
                thumbnail_path=video.thumbnail_path
            )
            results["YOUTUBE"] = yt_res

    await db.commit()
    await db.refresh(video)

    return {
        "video_id": video.id,
        "video_status": video.status,
        "results": results
    }
