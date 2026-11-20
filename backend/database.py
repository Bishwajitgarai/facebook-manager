import os
import logging
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import select, text
from backend.config import settings

logger = logging.getLogger("database")

is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    **({} if is_sqlite else {"pool_size": 10, "max_overflow": 20})
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info(f"Database schema initialized using { 'SQLite' if is_sqlite else 'PostgreSQL' }.")

async def migrate_from_sqlite_if_needed():
    """
    If running on PostgreSQL and an existing SQLite database exists at ./data/reelstudio.db,
    migrates existing videos, posts, and settings to PostgreSQL if the target table is empty.
    """
    if is_sqlite:
        return

    sqlite_path = Path("./data/reelstudio.db")
    if not sqlite_path.exists():
        return

    try:
        from backend.models import Video, PlatformPost, JobRun, Setting
        async with AsyncSessionLocal() as pg_session:
            # Check if PostgreSQL already has videos
            existing = await pg_session.execute(select(Video.id).limit(1))
            if existing.scalar() is not None:
                logger.info("PostgreSQL database already has records. Skipping SQLite migration.")
                return

            logger.info("Migrating existing data from SQLite to PostgreSQL...")
            # Connect to SQLite
            sqlite_engine = create_async_engine(f"sqlite+aiosqlite:///{sqlite_path.as_posix()}", echo=False)
            sqlite_session_maker = async_sessionmaker(bind=sqlite_engine, class_=AsyncSession)

            async with sqlite_session_maker() as sqlite_session:
                # Migrate Videos
                videos_res = await sqlite_session.execute(select(Video))
                old_videos = videos_res.scalars().all()
                for v in old_videos:
                    new_v = Video(
                        id=v.id,
                        uuid=v.uuid,
                        title=v.title,
                        topic=v.topic,
                        niche=v.niche,
                        hook=v.hook,
                        narration_text=v.narration_text,
                        caption=v.caption,
                        script_data=v.script_data,
                        status=v.status,
                        video_path=v.video_path,
                        audio_path=v.audio_path,
                        thumbnail_path=v.thumbnail_path,
                        duration_seconds=v.duration_seconds,
                        file_size_bytes=v.file_size_bytes,
                        resolution=v.resolution,
                        created_at=v.created_at,
                        updated_at=v.updated_at,
                        scheduled_for=v.scheduled_for,
                        error_message=v.error_message
                    )
                    pg_session.add(new_v)

                # Migrate PlatformPosts
                posts_res = await sqlite_session.execute(select(PlatformPost))
                old_posts = posts_res.scalars().all()
                for p in old_posts:
                    new_p = PlatformPost(
                        id=p.id,
                        video_id=p.video_id,
                        platform=p.platform,
                        status=p.status,
                        platform_post_id=p.platform_post_id,
                        platform_url=p.platform_url,
                        error_message=p.error_message,
                        posted_at=p.posted_at,
                        created_at=p.created_at
                    )
                    pg_session.add(new_p)

                # Migrate Settings
                settings_res = await sqlite_session.execute(select(Setting))
                old_settings = settings_res.scalars().all()
                for s in old_settings:
                    new_s = Setting(
                        key=s.key,
                        value=s.value,
                        description=s.description,
                        updated_at=s.updated_at
                    )
                    pg_session.add(new_s)

                await pg_session.commit()
                logger.info(f"Successfully migrated {len(old_videos)} videos and {len(old_posts)} posts from SQLite to PostgreSQL.")
            await sqlite_engine.dispose()
    except Exception as e:
        logger.warning(f"SQLite migration note: {e}")
