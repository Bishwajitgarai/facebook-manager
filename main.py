import uvicorn
from backend.config import settings

def main():
    print("""
===================================================================
      OMNIREELS STUDIO - AI VIDEO GENERATOR & SOCIAL SYNC
===================================================================
  * Local Storage:  ./storage (Videos, Audio, Visuals tracked locally)
  * Database:       SQLite (./data/reelstudio.db)
  * Daily Engine:   APScheduler (Auto-Generates & Syncs daily)
  * Target Social:  Facebook Reels & Video (Expandable to IG & YT)
  
  * Backend API:    http://127.0.0.1:8000
  * Swagger Docs:   http://127.0.0.1:8000/docs
  * Frontend UI:    http://127.0.0.1:3000 (Next.js) or http://127.0.0.1:8000
===================================================================
""")
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )

if __name__ == "__main__":
    main()
