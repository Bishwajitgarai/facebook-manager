import os
import json
import logging
from typing import Optional, Dict, Any, List
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from backend.config import settings
from backend.services.redis_service import redis_service

logger = logging.getLogger("gemini_service")

# Curated fallback viral scripts for offline testing or when API key is not provided yet
VIRAL_NICHES_DEFAULTS = {
    "Almost Real (Hyperrealistic Scenarios)": [
        {
            "title": "What If The Internet Went Completely Dark For 48 Hours?",
            "hook": "Within just 60 minutes of the global internet going dark, modern civilization would change forever.",
            "scenes": [
                {
                    "scene_number": 1,
                    "narration": "First, digital payments vanish instantly. Cash registers freeze, ATMs stop dispensing, and gas pumps shut down across entire continents.",
                    "visual_prompt": "Photorealistic vertical 9:16 documentary shot of a crowded rainy metropolis, store cash registers frozen with black screens, people looking at dead phones in confusion, 35mm film grain, hyperrealistic cinematic lighting",
                    "duration_est": 5.0
                },
                {
                    "scene_number": 2,
                    "narration": "By hour twelve, modern supply chains completely stall. Freight ships, automated warehouse cranes, and hospital supply lines have zero digital coordination.",
                    "visual_prompt": "Cinematic vertical realistic shot of massive shipping container port at dusk, giant cranes frozen in silence, fog rolling over cargo ships, photorealistic national geographic style",
                    "duration_est": 5.0
                },
                {
                    "scene_number": 3,
                    "narration": "And by day two, humanity realizes just how fragile our digital world truly is when stripped back to raw survival.",
                    "visual_prompt": "Cinematic realistic silhouette of people gathered around a warm radio receiver at night in a dim neighborhood under a clear starry sky, poignant atmospheric lighting, 8k documentary capture",
                    "duration_est": 5.0
                }
            ],
            "call_to_action": "How many days could you realistically survive without internet? Follow Almost Real for scenarios that make you question our world.",
            "caption": "⚠️ 48 hours without the digital grid. Could our modern world survive it? \n\n#AlmostReal #Hyperrealism #RealScenarios #WhatIf #AIRealism #Survival #Technology #Reels",
            "hashtags": ["AlmostReal", "Hyperrealism", "RealScenarios", "WhatIf", "AIRealism", "Technology", "Reels"]
        },
        {
            "title": "What The Pyramids Really Looked Like On Opening Day",
            "hook": "You have never seen the Great Pyramids the way ancient Egyptians actually saw them.",
            "scenes": [
                {
                    "scene_number": 1,
                    "narration": "Four thousand years ago, they were not rough brown stone. They were completely covered in mirror-polished white Tura limestone.",
                    "visual_prompt": "Hyperrealistic vertical 9:16 shot of the Great Pyramid of Giza in 2500 BC, covered in gleaming smooth white polished limestone blinding under the desert sun, lush green Nile riverbank in foreground, 8k documentary style",
                    "duration_est": 5.0
                },
                {
                    "scene_number": 2,
                    "narration": "At the very apex sat a solid gold electrum capstone, reflecting the morning sun so brilliantly it could be seen from thirty miles away.",
                    "visual_prompt": "Cinematic close-up of the glowing solid gold pyramidion capstone reflecting brilliant blinding sun rays, carved ancient hieroglyphs, photorealistic cinematic lighting, ultra-detailed",
                    "duration_est": 5.0
                },
                {
                    "scene_number": 3,
                    "narration": "Rising like a solid mountain of shining light from the fertile green Nile river, it looked more alien than humanly possible.",
                    "visual_prompt": "Breathtaking photorealistic historical panorama of ancient Giza with thriving green date palms, ceremonial wooden boats sailing on blue Nile waters, white gleaming pyramids shining like crystals, 8k masterpiece",
                    "duration_est": 5.0
                }
            ],
            "call_to_action": "Would you travel back in time to witness this? Follow Almost Real for daily historical realities brought to life.",
            "caption": "🏛️ What the Pyramids truly looked like when newly built. A shining monument of pure white limestone and gold. \n\n#AlmostReal #AncientHistory #PyramidsOfEgypt #RealScenarios #Archaeology #AIRealism #Reels",
            "hashtags": ["AlmostReal", "AncientHistory", "PyramidsOfEgypt", "RealScenarios", "History", "Reels"]
        }
    ],
    "Dreamy Pixels (Surreal AI Worlds)": [
        {
            "title": "The Floating Metropolis Above The Clouds",
            "hook": "What if there is an impossible city floating in the sky that human eyes were never meant to see?",
            "scenes": [
                {
                    "scene_number": 1,
                    "narration": "Suspended between two violet moons lies a metropolis anchored only by ancient magnetic crystals.",
                    "visual_prompt": "Cinematic vertical 9:16 shot of an ethereal floating sci-fi city above golden clouds, bioluminescent architecture, double moons, dreamlike surreal aesthetic, 8k render",
                    "duration_est": 5.0
                },
                {
                    "scene_number": 2,
                    "narration": "Waterfalls of liquid starlight cascade upward into the atmosphere, defying every law of gravity known to mankind.",
                    "visual_prompt": "Surreal glowing waterfalls flowing upward into space surrounded by floating ancient geometric runes and stardust, dreamlike hyperrealistic fantasy, dramatic lighting",
                    "duration_est": 5.0
                },
                {
                    "scene_number": 3,
                    "narration": "And whenever a dreamer on Earth falls into deep REM sleep, a new tower quietly appears on the horizon.",
                    "visual_prompt": "A lone wanderer in a glowing cosmic cloak standing on a crystal precipice looking at infinite surreal dream towers stretching into eternity, 8k masterpiece",
                    "duration_est": 5.0
                }
            ],
            "call_to_action": "Would you spend eternity here? Drop a comment below and follow Dreamy Pixels for daily voyages into the impossible.",
            "caption": "🌌 Welcome to the forgotten city above the clouds. Where dreams become architecture. \n\n#DreamyPixels #SurrealArt #AIArtwork #Dreamscapes #FantasyWorlds #VisualStorytelling #CosmicArt #Reels",
            "hashtags": ["DreamyPixels", "SurrealArt", "AIArtwork", "Dreamscapes", "FantasyWorlds", "CosmicArt", "Reels"]
        },
        {
            "title": "What Earth Looks Like Inside A Glass Nebula",
            "hook": "Close your eyes for one second... and imagine if the universe was made of blown glass.",
            "scenes": [
                {
                    "scene_number": 1,
                    "narration": "Astronomers peer through cosmic dust, only to discover an ocean planet sealed completely inside an interstellar crystal sphere.",
                    "visual_prompt": "Cinematic vertical 9:16 cosmic landscape of a radiant planet glowing inside an ornate blown-glass sphere floating in a deep purple nebula, hyperdetailed, 8k",
                    "duration_est": 5.0
                },
                {
                    "scene_number": 2,
                    "narration": "Bioluminescent whales swim across rings of liquid emerald, singing frequencies that can be heard across lightyears.",
                    "visual_prompt": "Giant translucent celestial creatures soaring through cosmic emerald aurora clouds in space, ethereal surreal dreamscape, vibrant neon colors",
                    "duration_est": 5.0
                },
                {
                    "scene_number": 3,
                    "narration": "A reminder that reality is far stranger, more fragile, and more beautiful than we could ever dream.",
                    "visual_prompt": "A breathtaking cosmic sunset reflecting across kaleidoscopic glass prisms in deep space, hyperrealistic octane render, vertical aesthetic",
                    "duration_est": 5.0
                }
            ],
            "call_to_action": "Save this reel to escape reality anytime. Follow Dreamy Pixels for daily dreamscapes.",
            "caption": "✨ What if the cosmos is just a delicate glass dream? \n\n#DreamyPixels #CosmicWonder #SurrealVisuals #AIArt #EtherealAesthetics #SpaceDream #Reels",
            "hashtags": ["DreamyPixels", "CosmicWonder", "SurrealVisuals", "AIArt", "SpaceDream", "Reels"]
        }
    ],
    "Tech & AI Horizons": [
        {
            "title": "Quantum Computing Just Shattered A New Barrier",
            "hook": "Wait... Did scientists just make quantum computers 100 times faster overnight?",
            "scenes": [
                {
                    "scene_number": 1,
                    "narration": "Researchers just demonstrated a quantum processor that solves problems in seconds that would take supercomputers 47 years.",
                    "visual_prompt": "Cinematic 9:16 vertical shot of a futuristic glowing cryogenic quantum computer with golden circuits and laser beams in a high-tech laboratory",
                    "duration_est": 5.0
                },
                {
                    "scene_number": 2,
                    "narration": "Instead of using fragile physical qubits, new topological braid technology prevents error rates from corrupting calculations.",
                    "visual_prompt": "Futuristic 3D holographic visualization of quantum particles braiding together, neon blue and violet lighting, 8k render",
                    "duration_est": 5.0
                },
                {
                    "scene_number": 3,
                    "narration": "This means unbreakable encryption, instant drug discovery, and artificial intelligence models beyond our current comprehension.",
                    "visual_prompt": "A cybernetic artificial intelligence neural network pulsating with light waves across a dark digital cosmos, hyperrealistic",
                    "duration_est": 5.0
                }
            ],
            "call_to_action": "Are we ready for quantum supremacy? Drop your thoughts below and follow for daily tech breakthroughs!",
            "caption": "⚡ Quantum computing just took a massive leap forward! Here's what you need to know about the new breakthrough. \n\n#QuantumComputing #TechNews #ArtificialIntelligence #FutureTech #Innovation #Reels",
            "hashtags": ["QuantumComputing", "TechNews", "ArtificialIntelligence", "FutureTech", "Reels"]
        },
        {
            "title": "3 AI Tools That Feel Illegal To Know in 2026",
            "hook": "If you are not using these 3 AI tools yet, you are working 10 times harder than you need to.",
            "scenes": [
                {
                    "scene_number": 1,
                    "narration": "First is an AI agent that automatically researches, outlines, and scripts entire video campaigns in under 30 seconds.",
                    "visual_prompt": "Cinematic glowing glass computer terminal showing real-time automated AI workflows, vertical 9:16 composition, futuristic aesthetic",
                    "duration_est": 5.0
                },
                {
                    "scene_number": 2,
                    "narration": "Second is a neural audio enhancer that turns cheap microphone recordings into studio-grade Dolby Atmos sound.",
                    "visual_prompt": "High-end studio microphone surrounded by floating soundwaves and golden acoustic particles in a dark aesthetic studio",
                    "duration_est": 5.0
                },
                {
                    "scene_number": 3,
                    "narration": "And third is an autonomous scheduler that synchronizes your content across Facebook, Instagram, and YouTube on pure autopilot.",
                    "visual_prompt": "Modern multi-screen workstation displaying viral analytics curves rising exponentially into the clouds, neon glow",
                    "duration_est": 5.0
                }
            ],
            "call_to_action": "Save this reel so you don't lose it, and follow for tomorrow's AI secret!",
            "caption": "🚀 3 Insane AI tools saving creators 20+ hours every week. Bookmark this before it gets buried! \n\n#AITools #ProductivityHacks #TechTips #ContentCreator #Automation #Reels",
            "hashtags": ["AITools", "ProductivityHacks", "TechTips", "ContentCreator", "Reels"]
        }
    ],
    "Mindset & Stoic Wisdom": [
        {
            "title": "Marcus Aurelius' Rule For Mental Peace",
            "hook": "Two thousand years ago, the most powerful emperor in the world wrote down this one sentence.",
            "scenes": [
                {
                    "scene_number": 1,
                    "narration": "You have power over your mind, not outside events. Realize this, and you will find instant strength.",
                    "visual_prompt": "Cinematic marble statue of Roman Emperor Marcus Aurelius in dramatic chiaroscuro lighting, vertical composition, hyperrealistic",
                    "duration_est": 5.0
                },
                {
                    "scene_number": 2,
                    "narration": "Most people waste 80 percent of their daily energy stressing over things they can never control: opinions, delays, and other people's chaos.",
                    "visual_prompt": "A lone silhouette standing calm in the center of a chaotic swirling stormy ancient colosseum, golden cinematic sunlight breaking through",
                    "duration_est": 5.0
                },
                {
                    "scene_number": 3,
                    "narration": "When you detach your peace of mind from external outcomes, you become genuinely invincible.",
                    "visual_prompt": "Golden sunrise over misty mountain peaks, minimalist aesthetic, epic scale, 8k masterpiece",
                    "duration_est": 5.0
                }
            ],
            "call_to_action": "Double tap if you needed this reminder today. Follow for daily mental clarity.",
            "caption": "🏛️ The Stoic key to absolute calm in a chaotic world. \n\n#Stoicism #MarcusAurelius #Mindset #DailyDiscipline #InnerPeace #Wisdom #Reels",
            "hashtags": ["Stoicism", "MarcusAurelius", "Mindset", "DailyDiscipline", "Wisdom"]
        }
    ]
}

class GeminiService:
    def __init__(self):
        self._client = None

    async def get_config(self):
        api_key = await redis_service.get_setting("GEMINI_API_KEY", settings.GEMINI_API_KEY)
        model_name = await redis_service.get_setting("GEMINI_MODEL", settings.GEMINI_MODEL)
        return api_key, model_name

    async def _get_client(self):
        api_key, _ = await self.get_config()
        if self._client is None and api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=api_key)
            except Exception as e:
                logger.error(f"Error initializing Google GenAI Client: {e}")
        return self._client

    async def generate_reel_script(self, niche: str, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Uses Gemini to generate a high-retention viral short/reel script with:
        - Hook
        - 3-4 scenes with narration and precise visual prompts
        - Call to Action
        - Caption & Hashtags
        """
        client = await self._get_client()
        api_key, model_name = await self.get_config()

        if client and api_key:
            try:
                prompt_text = f"""
You are an elite viral video strategist for Facebook Reels, Instagram Reels, and YouTube Shorts.
Generate a captivating 30 to 45-second vertical reel script.

Target Niche: {niche}
Custom Topic: {topic if topic else "Pick the most fascinating, trending, and viral topic in this niche"}

Format rules:
- HOOK: The first sentence MUST be an irresistible pattern-interrupt curiosity hook (under 12 words).
- SCENES: Exactly 3 to 4 scenes. For each scene:
  - narration: 1-2 punchy, spoken sentences (rhythmic, exciting, conversational).
  - visual_prompt: Detailed prompt for generating a vertical 9:16 cinematic image (photorealistic, dramatic lighting, vivid color grading, 8k resolution).
  - duration_est: Approximate speech duration in seconds (between 4.0 and 6.0).
- CALL_TO_ACTION: A natural 1-sentence prompt for viewers to follow/comment/share.
- CAPTION: Engaging post caption with emojis and 5-7 trending hashtags.

Return ONLY a valid JSON object matching this schema:
{{
  "title": "Catchy 5-8 word title",
  "hook": "Spoken hook sentence",
  "scenes": [
    {{
      "scene_number": 1,
      "narration": "Text spoken in scene 1",
      "visual_prompt": "Cinematic visual description for AI image generator",
      "duration_est": 5.0
    }}
  ],
  "call_to_action": "Follow for daily...",
  "caption": "Full post text with #hashtags",
  "hashtags": ["tag1", "tag2"]
}}
"""
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt_text,
                    config={
                        "response_mime_type": "application/json"
                    }
                )
                
                text_content = response.text.strip()
                parsed = json.loads(text_content)
                logger.info(f"Successfully generated script via Gemini: {parsed.get('title')}")
                return parsed

            except Exception as e:
                logger.warning(f"Gemini API generation failed ({e}), falling back to curated viral database.")

        # Fallback to rich curated library
        niche_key = niche if niche in VIRAL_NICHES_DEFAULTS else "Tech & AI Horizons"
        choices = VIRAL_NICHES_DEFAULTS[niche_key]
        import random
        selected = random.choice(choices).copy()
        if topic:
            selected["title"] = f"{topic}: The Truth"
            selected["hook"] = f"Here is the truth about {topic} that almost nobody is talking about."
        return selected

    async def generate_scene_image(self, prompt: str, output_path: str, scene_num: int, title: str) -> str:
        """
        Attempts to generate image using Gemini Imagen 3 if available;
        Otherwise generates a high-definition, stylized 1080x1920 graphic card with rich typography & gradients.
        Guarantees reliable output without failing the video pipeline.
        """
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        client = self._get_client()
        # Attempt Imagen via Google GenAI if supported
        if client and self.api_key:
            try:
                # Check if generate_images is supported by the client
                if hasattr(client.models, "generate_images"):
                    result = client.models.generate_images(
                        model="imagen-3.0-generate-002",
                        prompt=f"{prompt}, vertical 9:16 ratio, hyperrealistic cinematic lighting, 8k resolution, photorealistic",
                        config=dict(
                            number_of_images=1,
                            aspect_ratio="9:16",
                            person_generation="ALLOW_ADULT"
                        )
                    )
                    if result.generated_images:
                        image_bytes = result.generated_images[0].image.image_bytes
                        with open(out_file, "wb") as f:
                            f.write(image_bytes)
                        logger.info(f"Generated scene image via Imagen 3: {output_path}")
                        return str(out_file)
            except Exception as e:
                logger.info(f"Imagen generation unavailable ({e}), rendering high-impact procedural backdrop.")

        # Render high-resolution procedural 1080x1920 vertical visual card
        self._render_procedural_scene_image(prompt, str(out_file), scene_num, title)
        return str(out_file)

    def _render_procedural_scene_image(self, prompt: str, output_path: str, scene_num: int, title: str):
        """Creates an aesthetic, studio-quality 1080x1920 vertical visual banner with modern gradient & card design"""
        width, height = 1080, 1920
        # Color palettes based on scene
        palettes = [
            [(10, 15, 30), (25, 45, 90), (0, 210, 255)],     # Cyber Blue
            [(20, 10, 30), (80, 20, 90), (255, 90, 150)],    # Neon Purple
            [(15, 25, 20), (20, 70, 50), (0, 255, 170)],     # Emerald Matrix
            [(25, 15, 10), (90, 45, 15), (255, 170, 0)],     # Solar Amber
        ]
        bg_dark, bg_mid, accent = palettes[(scene_num - 1) % len(palettes)]

        # Generate smooth vertical gradient
        img = Image.new("RGB", (width, height), bg_dark)
        draw = ImageDraw.Draw(img)

        # Draw smooth vertical color gradient
        for y in range(height):
            ratio = y / height
            r = int(bg_dark[0] * (1 - ratio) + bg_mid[0] * ratio)
            g = int(bg_dark[1] * (1 - ratio) + bg_mid[1] * ratio)
            b = int(bg_dark[2] * (1 - ratio) + bg_mid[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Add decorative geometric grid / particles
        import math
        for i in range(15):
            cx = (i * 73) % width
            cy = (i * 137) % height
            rad = 80 + (i * 20) % 200
            draw.ellipse(
                [(cx - rad, cy - rad), (cx + rad, cy + rad)],
                outline=(accent[0], accent[1], accent[2]),
                width=1
            )

        # Center focus card
        card_margin = 80
        card_top = 400
        card_bottom = 1520
        # Card background with subtle fill
        draw.rectangle(
            [(card_margin, card_top), (width - card_margin, card_bottom)],
            fill=(bg_dark[0], bg_dark[1], bg_dark[2]),
            outline=accent,
            width=3
        )

        # Header Badge
        badge_text = f"SCENE 0{scene_num} • BREAKTHROUGH"
        draw.rectangle(
            [(card_margin + 40, card_top + 40), (card_margin + 360, card_top + 95)],
            fill=accent
        )
        draw.text((card_margin + 60, card_top + 55), badge_text, fill=(0, 0, 0))

        # Title / Topic text wrapping
        words = title.split()
        lines = []
        cur_line = []
        for w in words:
            cur_line.append(w)
            if len(" ".join(cur_line)) > 20:
                lines.append(" ".join(cur_line))
                cur_line = []
        if cur_line:
            lines.append(" ".join(cur_line))

        y_offset = card_top + 160
        for line in lines[:3]:
            draw.text((card_margin + 50, y_offset), line, fill=(255, 255, 255))
            y_offset += 65

        # Visual description abstract summary inside card
        draw.line(
            [(card_margin + 50, y_offset + 30), (width - card_margin - 50, y_offset + 30)],
            fill=(100, 100, 120),
            width=1
        )
        y_offset += 70

        # Draw prompt keywords
        prompt_words = prompt[:160] + "..." if len(prompt) > 160 else prompt
        p_lines = [prompt_words[i:i+32] for i in range(0, len(prompt_words), 32)]
        for pl in p_lines[:4]:
            draw.text((card_margin + 50, y_offset), pl, fill=(180, 200, 230))
            y_offset += 50

        # Bottom watermark / handle
        draw.text(
            (card_margin + 50, card_bottom - 80),
            "OmniReels Studio • Auto-Generated Daily",
            fill=(150, 160, 180)
        )

        img.save(output_path, quality=95)
        return output_path

gemini_service = GeminiService()
