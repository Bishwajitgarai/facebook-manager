from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseSocialPublisher(ABC):
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Name of the platform, e.g. FACEBOOK, INSTAGRAM, YOUTUBE"""
        pass

    @abstractmethod
    async def publish_video(
        self,
        video_path: str,
        title: str,
        caption: str,
        thumbnail_path: str = None
    ) -> Dict[str, Any]:
        """
        Publishes video file to platform and returns:
        {
            "success": bool,
            "post_id": Optional[str],
            "post_url": Optional[str],
            "error": Optional[str]
        }
        """
        pass

    @abstractmethod
    async def verify_connection(self) -> Dict[str, Any]:
        """
        Verifies credentials, tokens and permissions.
        Returns connection status info.
        """
        pass
