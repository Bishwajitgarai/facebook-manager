# 🎬 OmniReels Studio

> **Autonomous AI Video Creation & Social Sync Studio**  
> Generate high-retention 9:16 vertical Reels daily using your **Google Gemini** subscription, voice them with neural TTS, assemble them with dynamic Ken-Burns visual motion, and auto-post directly to your **Facebook Page** (with ready adapters for Instagram Reels & YouTube Shorts).

Every video is permanently tracked and stored on your local machine with full SQLite synchronization.

---

## ⚡ Quick Start

### 1. Configure Credentials
Copy `.env.example` to `.env` and fill in your Gemini and Facebook Page credentials:
```bash
cp .env.example .env
```

### 2. Launch OmniReels Studio

Choose how you want to run the studio:

#### Option A: Foreground Execution (Standard Terminal)
```bash
uv run main.py
```

#### Option B: Windows PowerShell Background Daemon (`maintain.ps1`)
Run in the background without keeping a terminal window open:
```powershell
# 1. Start the Studio in the background
.\maintain.ps1 start

# 2. Check if the server & daily scheduler are running
.\maintain.ps1 status

# 3. View live application logs (Press Ctrl+C to exit log view)
.\maintain.ps1 logs

# 4. Stop the background process
.\maintain.ps1 stop

# 5. Restart the server
.\maintain.ps1 restart
```
> **Tip for Windows script permissions**: If you see *"Script execution is disabled"*, run once:  
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`  
> Or prefix with bypass: `powershell -ExecutionPolicy Bypass -File .\maintain.ps1 start`

#### Option C: Linux / VPS / WSL Background Daemon with Tmux (`maintain.sh`)
```bash
# Start in background detached tmux session
./maintain.sh start

# Check status & health
./maintain.sh status

# Attach to live terminal console
./maintain.sh attach      # Detach with: Ctrl+b then d

# View live application logs
./maintain.sh logs

# Stop or restart
./maintain.sh stop
./maintain.sh restart
```

* **Interactive Web Dashboard**: [http://localhost:8000](http://localhost:8000) or [http://localhost:3000](http://localhost:3000)
* **Interactive API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🌟 Key Features

* 🧠 **Gemini Prompt Strategy**: Automatically crafts 3-second pattern-interrupt hooks, scene-by-scene spoken narrations, cinematic visual prompts, engaging captions, and viral hashtags.
* 🎙️ **Studio-Grade Neural Voiceover**: Free, natural neural text-to-speech powered by Edge-TTS (Christopher, Jenny, Guy, Aria, Ryan).
* 🎥 **Bundled Video Engine**: Self-contained H.264/AAC 1080x1920 (9:16) compiler with Ken-Burns pan/zoom motion. **No external ffmpeg installation required!**
* 💾 **Local Machine Storage & Sync**: Every video (`.mp4`), audio track (`.mp3`), and visual thumbnail is saved locally in `./storage/` and indexed in `./data/reelstudio.db` using SQLite.
* ⏰ **Autonomous Daily Scheduler**: Background APScheduler triggers daily video generation at your chosen time (e.g., 10:00 AM) and auto-publishes to Facebook.
* 📱 **Multi-Platform Architecture**: Facebook Graph API v21.0 live uploader + prepared adapters for Instagram Reels and YouTube Shorts.
* 💻 **Next.js & Tailwind Dashboard**: Responsive dark-mode dashboard with custom vertical Reel video player, one-click manual publishing, script inspector, and Facebook status validator.

---

## 🚀 Setting Up Your Facebook Page & API Token

To auto-post to Facebook:
1. **Create or Choose a Facebook Page**:
   * Suggested names below in the [Viral Niche Ideas](#-recommended-facebook-page-names) section.
2. **Meta for Developers**:
   * Visit [developers.facebook.com](https://developers.facebook.com/) and click **My Apps** > **Create App**.
   * Select **Other** > **Business**.
   * Name your app (e.g., `OmniReels Studio`).
3. **Generate Page Access Token**:
   * Open the **Graph API Explorer** tool (`developers.facebook.com/tools/explorer`).
   * Select your Meta App.
   * In **User or Page**, select your Facebook Page.
   * Add the following Permissions:
     * `pages_show_list`
     * `pages_read_engagement`
     * `pages_manage_posts`
   * Click **Generate Access Token**.
   * To convert this to a **Never-Expiring Long-Lived Token**, use the Access Token Tool debugger (`developers.facebook.com/tools/debug/accesstoken`).
4. **Find your Page ID**:
   * Open your Facebook Page > **About** > **Page Transparency** or **Settings** to copy your numeric `Page ID`.
5. **Add to `.env`**:
   ```env
   FACEBOOK_PAGE_ID=your_page_id_here
   FACEBOOK_PAGE_ACCESS_TOKEN=your_page_access_token_here
   ```

---

## 💡 Flagship Brand: Almost Real

| Brand | Recommended Page Name | Catchy Slogan / Bio |
| :--- | :--- | :--- |
| **Flagship Pick** | **Almost Real** | *"Real-world scenarios, historical moments, and future realities brought to life with AI. 🌐 Daily 60-second visual experiences."* |
| **Curiosity Alternative** | `Curious Matrix` | *"Exploring anomalies in science, technology, and our world."* |
| **Cinematic Alternative** | `Parallel Earth` | *"What our world would look like in different times and realities."* |
| **Mindset Alternative** | `Iron Mindset Lab` | *"Timeless Stoic wisdom and mental models for high achievers."* |

---

## 📂 Project Architecture

```
facebook-manager/
├── backend/
│   ├── api/                  # FastAPI REST endpoints
│   │   ├── generate.py       # Trigger Reel creation & script previews
│   │   ├── publish.py        # Social media publishing & token verification
│   │   ├── schedule.py       # Daily schedule management & manual run triggers
│   │   ├── stats.py          # Dashboard storage and video metrics
│   │   └── videos.py         # Stored video streaming, details, and delete
│   ├── services/
│   │   ├── gemini_service.py # Gemini 2.5 Flash script & visual prompt engine
│   │   ├── tts_service.py    # Edge-TTS neural voiceover generator
│   │   ├── video_engine.py   # Bundled FFmpeg 9:16 vertical video compiler
│   │   └── social/           # Platform publishing adapters
│   │       ├── facebook.py   # Facebook Graph API Page video/reel uploader
│   │       ├── instagram.py  # Instagram Reels container adapter
│   │       └── youtube.py    # YouTube Shorts adapter
│   ├── config.py             # Pydantic Settings & environment validation
│   ├── database.py           # SQLite aiosqlite engine & session maker
│   ├── models.py             # SQLAlchemy models (Video, PlatformPost, JobRun)
│   ├── scheduler.py          # APScheduler daily autonomous cron job
│   └── main.py               # FastAPI application lifecycle & static hosting
├── frontend/                 # Modern Next.js 15+ & Tailwind CSS Dashboard
│   ├── app/
│   │   ├── page.tsx          # Interactive dashboard with 9:16 Reel player
│   │   └── globals.css       # Tailwind CSS styling
│   └── package.json
├── storage/                  # Local media sync folder
│   ├── videos/               # Rendered 1080x1920 .mp4 videos
│   ├── audio/                # Synthesized .mp3 voice tracks
│   └── images/               # Scene graphics & thumbnails
├── data/                     # Local SQLite database (reelstudio.db)
├── .env.example              # Documented environment template
├── .gitignore                # Excludes private tokens, videos, and database
├── pyproject.toml            # uv project configuration
└── main.py                   # Master entrypoint: `uv run main.py`
```

---

## ⚙️ Environment Variables Reference

| Variable | Description | Default |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Your Google Gemini API Key | *(Required)* |
| `GEMINI_MODEL` | Gemini text model | `gemini-2.5-flash` |
| `FACEBOOK_PAGE_ID` | Numeric Facebook Page ID | `""` |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | Meta Graph API Page Access Token | `""` |
| `DAILY_SCHEDULE_HOUR` | 24-hour format hour for daily auto-run | `10` |
| `DAILY_SCHEDULE_MINUTE` | Minute for daily auto-run | `0` |
| `AUTO_PUBLISH_FACEBOOK` | Instantly publish on render without review | `false` |
| `DEFAULT_NICHE` | Target content niche | `Almost Real (Hyperrealistic Scenarios)` |
| `DEFAULT_VOICE` | Edge-TTS neural narrator voice | `en-US-ChristopherNeural` |
| `STORAGE_DIR` | Local folder for videos, audio, images | `./storage` |
| `DATABASE_URL` | SQLite database file location | `sqlite+aiosqlite:///./data/reelstudio.db` |

---

## 🛠️ Development & Running Commands

* **Start Fullstack Studio (Foreground)**:
  ```bash
  uv run main.py
  ```
* **Windows PowerShell Background Runner**:
  ```powershell
  .\maintain.ps1 start    # Run background daemon
  .\maintain.ps1 status   # Check status & health
  .\maintain.ps1 logs     # Tail live logs
  .\maintain.ps1 stop     # Stop daemon
  ```
* **Linux / Tmux Background Runner**:
  ```bash
  ./maintain.sh start     # Run in tmux
  ./maintain.sh status    # Check status
  ./maintain.sh logs      # Tail live logs
  ./maintain.sh attach    # View interactive terminal
  ./maintain.sh stop      # Stop daemon
  ```
* **Run Frontend in Dev Mode (with Hot Reload)**:
  ```bash
  cd frontend
  npm run dev
  ```
* **Rebuild Frontend Static Assets**:
  ```bash
  cd frontend
  npm run build
  ```

---

## 🔒 Privacy & Local Sync

All videos, voiceovers, thumbnails, and SQLite records remain strictly on your local machine in the `storage/` and `data/` directories. Your `.env` and media files are strictly protected by `.gitignore`.
