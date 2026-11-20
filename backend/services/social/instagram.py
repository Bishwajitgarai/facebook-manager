import os
import httpx
import logging
from typing import Dict, Any, Optional
from backend.services.social.base import BaseSocialPublisher
from backend.config import settings

logger = logging.getLogger("instagram_publisher")

class InstagramPublisher(BaseSocialPublisher):
    """
    Instagram Reels Publisher using Instagram Graph API:
    1. Create Media Container: POST /{ig-user-id}/media (media_type=REELS, video_url=...)
    2. Wait for status_code == FINISHED: GET /{container-id}?fields=status_code
    3. Publish Container: POST /{ig-user-id}/media_publish (creation_id=...)
    """
    @property
    def platform_name(self) -> str:
        return "INSTAGRAM"

    def __init__(self):
        self.account_id = settings.INSTAGRAM_ACCOUNT_ID
        self.access_token = settings.INSTAGRAM_ACCESS_TOKEN
        self.api_version = "v21.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    async def verify_connection(self) -> Dict[str, Any]:
        if not self.account_id or not self.access_token:
            return {
                "connected": False,
                "message": "Instagram Business Account ID or Access Token not configured (Ready for activation)"
            }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(
                    f"{self.base_url}/{self.account_id}",
                    params={"access_token": self.access_token, "fields": "id,username,name,followers_count"}
                )
                if res.status_code == 200:
                    data = res.json()
                    return {
                        "connected": True,
                        "username": data.get("username"),
                        "followers": data.get("followers_count", 0),
                        "message": f"Connected to Instagram Account @{data.get('username')}"
                    }
                return {"connected": False, "message": res.text}
        except Exception as e:
            return {"connected": False, "message": str(e)}

    async def publish_video(
        self,
        video_path: str,
        title: str,
        caption: str,
        thumbnail_path: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.account_id or not self.access_token:
            return {
                "success": False,
                "error": "Instagram credentials not yet configured in .env",
                "post_id": None,
                "post_url": None
            }
        return {
            "success": False,
            "error": "Instagram Reels requires public media hosting URL for container ingest. Local sync active.",
            "post_id": None,
            "post_url": None
        }

instagram_publisher = InstagramPublisher()
