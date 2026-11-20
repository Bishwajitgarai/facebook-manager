import os
import httpx
import logging
from typing import Dict, Any, Optional
from backend.services.social.base import BaseSocialPublisher
from backend.config import settings
from backend.services.redis_service import redis_service

logger = logging.getLogger("facebook_publisher")

class FacebookPublisher(BaseSocialPublisher):
    @property
    def platform_name(self) -> str:
        return "FACEBOOK"

    def __init__(self):
        self.api_version = "v21.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    async def get_credentials(self):
        page_id = await redis_service.get_setting("FACEBOOK_PAGE_ID", settings.FACEBOOK_PAGE_ID)
        token = await redis_service.get_setting("FACEBOOK_PAGE_ACCESS_TOKEN", settings.FACEBOOK_PAGE_ACCESS_TOKEN)
        return page_id, token

    async def verify_connection(self) -> Dict[str, Any]:
        """Verifies if the Facebook Page ID and Page Access Token are valid and have posting permissions"""
        page_id, access_token = await self.get_credentials()
        if not page_id or not access_token:
            return {
                "connected": False,
                "message": "Facebook Page ID or Page Access Token is missing in .env / Redis cache"
            }

        url = f"{self.base_url}/{page_id}"
        params = {
            "access_token": access_token,
            "fields": "id,name,link,fan_count,is_published"
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(url, params=params)
                data = res.json()

                if res.status_code == 200:
                    return {
                        "connected": True,
                        "page_id": data.get("id"),
                        "page_name": data.get("name"),
                        "page_link": data.get("link"),
                        "followers": data.get("fan_count", 0),
                        "message": f"Successfully connected to Facebook Page: {data.get('name')}"
                    }
                else:
                    error_detail = data.get("error", {}).get("message", "Unknown Facebook API error")
                    return {
                        "connected": False,
                        "error": error_detail,
                        "message": f"Facebook API Error ({res.status_code}): {error_detail}"
                    }
        except Exception as e:
            logger.error(f"Failed to connect to Facebook: {e}")
            return {
                "connected": False,
                "error": str(e),
                "message": f"Network error connecting to Facebook API: {str(e)}"
            }

    async def publish_video(
        self,
        video_path: str,
        title: str,
        caption: str,
        thumbnail_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Uploads and publishes a video/Reel directly to the target Facebook Page
        using Facebook Graph API v21.0 video upload endpoint.
        """
        page_id, access_token = await self.get_credentials()
        if not page_id or not access_token:
            return {
                "success": False,
                "error": "Facebook Page ID or Page Access Token not configured in .env or Redis cache",
                "post_id": None,
                "post_url": None
            }

        if not os.path.exists(video_path):
            return {
                "success": False,
                "error": f"Video file not found at path: {video_path}",
                "post_id": None,
                "post_url": None
            }

        upload_url = f"{self.base_url}/{page_id}/videos"
        logger.info(f"Uploading video '{title}' to Facebook Page {page_id}...")

        try:
            # Prepare multipart upload
            file_name = os.path.basename(video_path)
            with open(video_path, "rb") as video_file:
                files = {
                    "source": (file_name, video_file, "video/mp4")
                }
                data = {
                    "access_token": access_token,
                    "title": title[:255],
                    "description": caption,
                    "published": "true"
                }

                # Video upload can take up to 2-3 minutes for large videos
                async with httpx.AsyncClient(timeout=180.0) as client:
                    response = await client.post(upload_url, data=data, files=files)
                    resp_json = response.json()

                    if response.status_code == 200 and "id" in resp_json:
                        video_id = resp_json["id"]
                        post_url = f"https://www.facebook.com/{self.page_id}/videos/{video_id}/"
                        logger.info(f"Video successfully published to Facebook! Video ID: {video_id}")
                        return {
                            "success": True,
                            "post_id": video_id,
                            "post_url": post_url,
                            "error": None
                        }
                    else:
                        error_msg = resp_json.get("error", {}).get("message", f"HTTP {response.status_code}: {response.text}")
                        logger.error(f"Facebook video upload failed: {error_msg}")
                        return {
                            "success": False,
                            "error": error_msg,
                            "post_id": None,
                            "post_url": None
                        }

        except Exception as e:
            logger.error(f"Exception during Facebook video upload: {e}")
            return {
                "success": False,
                "error": str(e),
                "post_id": None,
                "post_url": None
            }

facebook_publisher = FacebookPublisher()
