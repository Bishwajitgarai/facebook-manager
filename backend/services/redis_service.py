import json
import logging
from typing import Optional, Any, Dict
import redis.asyncio as aioredis
from backend.config import settings

logger = logging.getLogger("redis_service")

class RedisService:
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self._client: Optional[aioredis.Redis] = None

    async def get_client(self) -> Optional[aioredis.Redis]:
        """Returns active Redis client or None if Redis is unreachable, without throwing exceptions"""
        if self._client is None:
            try:
                self._client = aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=2.0,
                    socket_timeout=2.0
                )
                await self._client.ping()
                logger.info("Connected to Redis cache & message broker successfully.")
            except Exception as e:
                logger.warning(f"Redis unavailable ({e}). Operating in memory/env fallback mode.")
                self._client = None
        return self._client

    async def sync_env_to_redis(self) -> bool:
        """Loads critical configuration from .env into Redis cache on startup"""
        client = await self.get_client()
        if not client:
            return False

        try:
            config_map: Dict[str, str] = {
                "GEMINI_API_KEY": str(settings.GEMINI_API_KEY or ""),
                "GEMINI_MODEL": str(settings.GEMINI_MODEL or "gemini-2.5-flash"),
                "FACEBOOK_PAGE_ID": str(settings.FACEBOOK_PAGE_ID or ""),
                "FACEBOOK_PAGE_ACCESS_TOKEN": str(settings.FACEBOOK_PAGE_ACCESS_TOKEN or ""),
                "INSTAGRAM_ACCOUNT_ID": str(settings.INSTAGRAM_ACCOUNT_ID or ""),
                "INSTAGRAM_ACCESS_TOKEN": str(settings.INSTAGRAM_ACCESS_TOKEN or ""),
                "YOUTUBE_CLIENT_ID": str(settings.YOUTUBE_CLIENT_ID or ""),
                "YOUTUBE_CLIENT_SECRET": str(settings.YOUTUBE_CLIENT_SECRET or ""),
                "DAILY_SCHEDULE_HOUR": str(settings.DAILY_SCHEDULE_HOUR),
                "DAILY_SCHEDULE_MINUTE": str(settings.DAILY_SCHEDULE_MINUTE),
                "AUTO_PUBLISH_FACEBOOK": "true" if settings.AUTO_PUBLISH_FACEBOOK else "false",
                "DEFAULT_NICHE": str(settings.DEFAULT_NICHE or "Almost Real (Hyperrealistic Scenarios)"),
                "DEFAULT_VOICE": str(settings.DEFAULT_VOICE or "en-US-ChristopherNeural"),
            }

            for key, val in config_map.items():
                await client.set(f"config:{key}", val)
            await client.set("config:all", json.dumps(config_map))
            logger.info("Synchronized environment variables into Redis cache.")
            return True
        except Exception as e:
            logger.warning(f"Failed to sync env to Redis: {e}")
            return False

    async def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Retrieves setting:
        1. Checks Redis first (cached from .env or dynamically updated)
        2. Falls back to settings object (.env) if Redis is down or key missing
        """
        try:
            client = await self.get_client()
            if client:
                val = await client.get(f"config:{key}")
                if val is not None:
                    # Convert boolean strings if needed
                    if val.lower() == "true":
                        return True
                    if val.lower() == "false":
                        return False
                    return val
        except Exception as e:
            logger.debug(f"Redis get_setting error for {key}: {e}. Falling back to env.")
            self._client = None

        # Fallback to local settings / .env
        return getattr(settings, key, default)

    async def set_setting(self, key: str, value: Any) -> bool:
        """Dynamically updates a setting in Redis cache"""
        try:
            client = await self.get_client()
            if client:
                val_str = str(value)
                await client.set(f"config:{key}", val_str)
                return True
        except Exception as e:
            logger.debug(f"Redis set_setting error for {key}: {e}")
            self._client = None
        return False

    async def set_task_status(self, task_id: str, status: str, message: str, progress: int = 0):
        try:
            client = await self.get_client()
            if client:
                data = json.dumps({
                    "task_id": task_id,
                    "status": status,
                    "message": message,
                    "progress": progress
                })
                await client.setex(f"task:{task_id}", 3600, data)
        except Exception:
            self._client = None

    async def get_task_status(self, task_id: str) -> Optional[dict]:
        try:
            client = await self.get_client()
            if client:
                raw = await client.get(f"task:{task_id}")
                if raw:
                    return json.loads(raw)
        except Exception:
            self._client = None
        return None

    async def check_health(self) -> bool:
        try:
            client = await self.get_client()
            if client:
                return await client.ping()
        except Exception:
            self._client = None
            return False
        return False

    async def close(self):
        if self._client:
            try:
                await self._client.aclose()
            except Exception:
                pass
            self._client = None

redis_service = RedisService()
