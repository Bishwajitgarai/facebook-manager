from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class SceneItem(BaseModel):
    scene_number: int
    narration: str
    visual_prompt: str
    duration_est: float = 5.0

class ScriptData(BaseModel):
    title: str
    hook: str
    scenes: List[SceneItem]
    call_to_action: str
    caption: str
    hashtags: List[str] = []

class GenerateVideoRequest(BaseModel):
    topic: Optional[str] = Field(default=None, description="Custom topic or leave empty for auto niche curation")
    niche: Optional[str] = Field(default="Tech & AI Horizons", description="Target niche")
    voice: Optional[str] = Field(default="en-US-ChristopherNeural", description="Edge TTS Neural voice")
    auto_publish_facebook: Optional[bool] = Field(default=False, description="Whether to immediately post after render")

class PlatformPostResponse(BaseModel):
    id: int
    platform: str
    status: str
    platform_post_id: Optional[str] = None
    platform_url: Optional[str] = None
    error_message: Optional[str] = None
    posted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VideoResponse(BaseModel):
    id: int
    uuid: str
    title: str
    topic: str
    niche: str
    hook: Optional[str] = None
    narration_text: Optional[str] = None
    caption: Optional[str] = None
    status: str
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    duration_seconds: float
    file_size_bytes: int
    resolution: str
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    posts: List[PlatformPostResponse] = []

    class Config:
        from_attributes = True

class PublishRequest(BaseModel):
    platforms: List[str] = Field(default=["FACEBOOK"], description="Target platforms e.g. ['FACEBOOK', 'INSTAGRAM', 'YOUTUBE']")
    custom_caption: Optional[str] = None

class SchedulerConfigRequest(BaseModel):
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)
    auto_publish: bool
    niche: str

class StatsResponse(BaseModel):
    total_videos: int
    ready_videos: int
    posted_videos: int
    total_storage_mb: float
    next_scheduled_run: Optional[str] = None
    last_run_status: Optional[str] = None
    facebook_connected: bool
    gemini_connected: bool
