from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    # Gemini API
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key")
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash", description="Gemini text model")

    # Facebook API
    FACEBOOK_PAGE_ID: str = Field(default="", description="Facebook Page ID")
    FACEBOOK_PAGE_ACCESS_TOKEN: str = Field(default="", description="Facebook Page Access Token")

    # Instagram API (Optional for future)
    INSTAGRAM_ACCOUNT_ID: Optional[str] = Field(default=None)
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = Field(default=None)

    # YouTube API (Optional for future)
    YOUTUBE_CLIENT_ID: Optional[str] = Field(default=None)
    YOUTUBE_CLIENT_SECRET: Optional[str] = Field(default=None)

    # Scheduler & Automation
    DAILY_SCHEDULE_HOUR: int = Field(default=10, ge=0, le=23)
    DAILY_SCHEDULE_MINUTE: int = Field(default=0, ge=0, le=59)
    AUTO_PUBLISH_FACEBOOK: bool = Field(default=False)

    # Defaults
    DEFAULT_NICHE: str = Field(default="Almost Real (Hyperrealistic Scenarios)")
    DEFAULT_VOICE: str = Field(default="en-US-ChristopherNeural")

    # Storage & DB (PostgreSQL & SQLite)
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/reelstudio.db",
        description="Async SQLAlchemy database URL (PostgreSQL or SQLite)"
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for caching & background events"
    )
    API_V1_STR: str = "/api/v1"
    STORAGE_DIR: str = Field(default="./storage")
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    FRONTEND_URL: str = Field(default="http://localhost:3000")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

    @property
    def storage_path(self) -> Path:
        p = Path(self.STORAGE_DIR)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def videos_path(self) -> Path:
        p = self.storage_path / "videos"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def audio_path(self) -> Path:
        p = self.storage_path / "audio"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def images_path(self) -> Path:
        p = self.storage_path / "images"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def data_path(self) -> Path:
        p = Path("./data")
        p.mkdir(parents=True, exist_ok=True)
        return p

settings = Settings()
# Initialize directories upon configuration load
_ = settings.videos_path
_ = settings.audio_path
_ = settings.images_path
_ = settings.data_path
