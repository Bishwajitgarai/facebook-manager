from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.database import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    topic = Column(String(255), nullable=False)
    niche = Column(String(100), default="Tech & AI Horizons")
    
    # Script & Creative Content
    hook = Column(Text, nullable=True)
    narration_text = Column(Text, nullable=True)
    caption = Column(Text, nullable=True)
    script_data = Column(JSON, nullable=True) # Full structured breakdown (scenes, prompts)
    
    # Local Files & Media Specs
    status = Column(String(50), default="GENERATING", index=True) # GENERATING, READY, POSTED, FAILED
    video_path = Column(String(500), nullable=True)
    audio_path = Column(String(500), nullable=True)
    thumbnail_path = Column(String(500), nullable=True)
    duration_seconds = Column(Float, default=0.0)
    file_size_bytes = Column(Integer, default=0)
    resolution = Column(String(20), default="1080x1920") # 9:16 vertical standard
    
    # Metadata & Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    scheduled_for = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    posts = relationship("PlatformPost", back_populates="video", cascade="all, delete-orphan")
    job_runs = relationship("JobRun", back_populates="video")

class PlatformPost(Base):
    __tablename__ = "platform_posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False) # FACEBOOK, INSTAGRAM, YOUTUBE
    status = Column(String(50), default="PENDING") # PENDING, SUCCESS, FAILED
    platform_post_id = Column(String(255), nullable=True)
    platform_url = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    video = relationship("Video", back_populates="posts")

class JobRun(Base):
    __tablename__ = "job_runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_type = Column(String(50), default="DAILY_AUTOMATION") # DAILY_AUTOMATION, MANUAL_TRIGGER
    status = Column(String(50), default="RUNNING") # RUNNING, SUCCESS, FAILED
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="SET NULL"), nullable=True)
    logs = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    video = relationship("Video", back_populates="job_runs")

class Setting(Base):
    __tablename__ = "settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=True)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
