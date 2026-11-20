import os
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from backend.database import get_db
from backend.models import Video, PlatformPost
from backend.schemas import VideoResponse

router = APIRouter(prefix="/videos", tags=["Videos"])

@router.get("", response_model=List[VideoResponse])
async def list_videos(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Lists all stored videos with platform publishing details"""
    query = select(Video).options(selectinload(Video.posts)).order_by(Video.created_at.desc()).limit(limit)
    if status:
        query = query.where(Video.status == status)
    result = await db.execute(query)
    videos = result.scalars().all()
    return videos

@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: int, db: AsyncSession = Depends(get_db)):
    """Gets details for a specific video"""
    query = select(Video).options(selectinload(Video.posts)).where(Video.id == video_id)
    result = await db.execute(query)
    video = result.scalars().first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@router.get("/{video_id}/stream")
async def stream_video(video_id: int, db: AsyncSession = Depends(get_db)):
    """Streams video MP4 for in-browser video player"""
    query = select(Video).where(Video.id == video_id)
    result = await db.execute(query)
    video = result.scalars().first()
    if not video or not video.video_path or not os.path.exists(video.video_path):
        raise HTTPException(status_code=404, detail="Video file does not exist on disk")
    return FileResponse(
        video.video_path,
        media_type="video/mp4",
        filename=f"{video.uuid}.mp4"
    )

@router.get("/{video_id}/thumbnail")
async def get_thumbnail(video_id: int, db: AsyncSession = Depends(get_db)):
    """Returns video thumbnail image"""
    query = select(Video).where(Video.id == video_id)
    result = await db.execute(query)
    video = result.scalars().first()
    if not video or not video.thumbnail_path or not os.path.exists(video.thumbnail_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(video.thumbnail_path, media_type="image/jpeg")

@router.delete("/{video_id}")
async def delete_video(video_id: int, db: AsyncSession = Depends(get_db)):
    """Deletes video from database and local storage"""
    query = select(Video).where(Video.id == video_id)
    result = await db.execute(query)
    video = result.scalars().first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Remove files
    for path in [video.video_path, video.audio_path, video.thumbnail_path]:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass

    await db.delete(video)
    await db.commit()
    return {"message": "Video successfully deleted", "id": video_id}
