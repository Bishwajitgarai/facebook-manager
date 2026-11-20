import os
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import imageio_ffmpeg
from backend.config import settings

logger = logging.getLogger("video_engine")

class VideoEngine:
    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        logger.info(f"Using bundled FFmpeg binary: {self.ffmpeg_exe}")

    async def render_reel(
        self,
        video_uuid: str,
        image_paths: List[str],
        audio_path: str,
        duration: float,
        title: str
    ) -> Dict[str, Any]:
        """
        Renders a vertical (1080x1920) 9:16 Reel/Short video by combining:
        - Dynamic zooming scene images (Ken Burns effect)
        - Synchronized neural voiceover audio track
        - High-compatibility H.264 / AAC MP4 encoding
        """
        out_video_path = settings.videos_path / f"{video_uuid}.mp4"
        out_thumb_path = settings.images_path / f"{video_uuid}_thumb.jpg"

        if not image_paths:
            raise ValueError("No images provided for video rendering.")

        num_scenes = len(image_paths)
        # Ensure duration is at least 3 seconds
        safe_duration = max(duration, 3.0)
        scene_duration = safe_duration / num_scenes
        fps = 30
        frames_per_scene = int(scene_duration * fps)

        # Create temporary video clips for each scene with Ken Burns zoom effect
        temp_clips = []
        temp_dir = settings.storage_path / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            for idx, img_path in enumerate(image_paths):
                scene_clip = temp_dir / f"{video_uuid}_scene_{idx}.mp4"
                # FFmpeg command: zoom in slowly on 1080x1920 image
                # zoompan filter creates subtle zoom motion for engagement
                zoom_cmd = [
                    self.ffmpeg_exe,
                    "-y",
                    "-loop", "1",
                    "-i", str(img_path),
                    "-vf", (
                        f"scale=1080:1920,setsar=1,"
                        f"zoompan=z='min(zoom+0.001,1.10)':d={frames_per_scene}:"
                        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps}"
                    ),
                    "-t", f"{scene_duration:.2f}",
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    "-preset", "ultrafast",
                    str(scene_clip)
                ]
                
                res = subprocess.run(zoom_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
                if res.returncode != 0:
                    logger.warning(f"Zoompan failed ({res.stderr[:200]}), falling back to direct static clip")
                    # Fallback static clip if zoompan fails
                    fallback_cmd = [
                        self.ffmpeg_exe,
                        "-y",
                        "-loop", "1",
                        "-i", str(img_path),
                        "-t", f"{scene_duration:.2f}",
                        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1",
                        "-c:v", "libx264",
                        "-pix_fmt", "yuv420p",
                        "-preset", "ultrafast",
                        str(scene_clip)
                    ]
                    subprocess.run(fallback_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                temp_clips.append(str(scene_clip))

            # Create concat list file with resolved posix paths
            concat_list_file = temp_dir / f"{video_uuid}_concat.txt"
            with open(concat_list_file, "w", encoding="utf-8") as f:
                for clip in temp_clips:
                    clean_path = Path(clip).resolve().as_posix()
                    f.write(f"file '{clean_path}'\n")

            # Final merge: Concatenate video clips + merge Voiceover audio
            final_cmd = [
                self.ffmpeg_exe,
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_list_file),
                "-i", str(audio_path),
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "22",
                "-c:a", "aac",
                "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-shortest", # Stop exactly when the shorter stream ends
                "-movflags", "+faststart", # Enable streaming in browsers
                str(out_video_path)
            ]

            logger.info(f"Rendering final Reel to {out_video_path}")
            res = subprocess.run(final_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            if res.returncode != 0:
                logger.error(f"FFmpeg render failed with error: {res.stderr}")
                raise RuntimeError(f"FFmpeg render error: {res.stderr[-500:]}")

            # Generate thumbnail from first second of the generated video
            thumb_cmd = [
                self.ffmpeg_exe,
                "-y",
                "-ss", "00:00:01",
                "-i", str(out_video_path),
                "-vframes", "1",
                "-q:v", "2",
                str(out_thumb_path)
            ]
            subprocess.run(thumb_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Check output size
            file_size = os.path.getsize(out_video_path)

            logger.info(f"Reel successfully generated! Size: {file_size / (1024*1024):.2f} MB")
            return {
                "video_path": str(out_video_path),
                "thumbnail_path": str(out_thumb_path),
                "duration_seconds": safe_duration,
                "file_size_bytes": file_size,
                "resolution": "1080x1920"
            }

        finally:
            # Clean up temp files
            for clip in temp_clips:
                try:
                    if os.path.exists(clip):
                        os.remove(clip)
                except Exception:
                    pass
            try:
                if concat_list_file.exists():
                    concat_list_file.unlink()
            except Exception:
                pass

video_engine = VideoEngine()
