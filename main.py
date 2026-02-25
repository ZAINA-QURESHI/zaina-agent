import os
import random
import datetime
import requests
import time
from google import genai
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

# --- CONFIGURATION ---
# 1. MODEL CHECK: Using 'gemini-1.5-flash' for global stability (avoids 404 in EU/France).
MODEL_NAME = "gemini-1.5-flash"

TOPICS = [
    "algorithmic surveillance", "digital decay", "brutalist architecture",
    "decolonizing the cloud", "glitch aesthetics", "data sovereignty",
    "the ghost in the machine", "metaspace boundaries", "post-human archive",
    "the architecture of noise", "silicon colonialism"
]

def search_scavenge_assets(topic):
    """Scrape the web for image URLs. Correction: Handling DDGS version variations."""
    print(f"[SCAVENGER] Zaina is hunting for: {topic}")
    assets = []
    try:
        # Using the context manager to ensure the connection closes
        with DDGS() as ddgs:
            # max_results=8 is a safe limit to avoid rate limiting
            results = list(ddgs.images(topic, max_results=8))
            for r in results:
                if 'image' in r:
                    assets.append(r['image'])
    except Exception as e:
        print(f"[ERROR] Scavenging failed: {e}")
    return assets

def call_krea_api(prompt):
    """Krea.ai Integration. Correction: Timeout increased for generative processing."""
    api_key = os.environ.get("KREA_API_KEY")
    if not api_key:
        print("[WARNING] KREA_API_KEY missing. Skipping Krea synthesis.")
        return None
    
    print(f"[KREA] Synthesizing vision for: {prompt}")
    try:
        # Standard endpoint. Note: If Krea changes their REST structure, this is the primary point of failure.
        response = requests.post(
            "https://api.krea.ai/v1/generate", 
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "prompt": f"Brutalist art, red black white, high contrast, {prompt}",
                "model": "krea-realtime",
                "width": 512, 
                "height": 512
            },
            timeout=60 # Increased timeout for heavy generation
        )
        
        if response.status_code == 200:
            return response.json().get("image_url")
    except Exception as e:
        print(f"[ERROR] Krea request failed: {e}")
    return None

def generate_multimodal_collage(topic):
    """Multimodal Art Logic. Correction: Stripping markdown backticks from AI output."""
    gemini_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=gemini_key)
    
    scavenged_images = search_scavenge_assets(topic)
    scavenged_url = random.choice(scavenged_images) if scavenged_images else ""
    krea_url = call_krea_api(topic)
    
    prompt = f"""
    You are Zaina Qureshi. Create a MULTIMODAL COLLAGE about: '{topic}'.
    Context: Scavenged URL: {scavenged_url} | Krea URL: {krea_url if krea_url else "None"}
    Requirements:
    - Single <div> with 'relative overflow-hidden'.
    - Use <canvas> and a <script> for red/black generative math patterns.
    - Use Tailwind for brutalist typography.
    - Output ONLY HTML/Script. NO markdown formatting.
    """
    
    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        raw_html = response.text.strip()
        
        # CLEANUP: Remove backticks if Gemini ignores 'No markdown' instruction
        if raw_html.startswith("```"):
            lines = raw_html.split("\n")
            # Remove first and last lines (the ```html and ```)
            raw_html = "\n".join(lines[1:-1]) if len(lines) > 2 else raw_html.replace("```html", "").replace("```", "")
        
        return raw_html
    except Exception as e:
        print(f"[ERROR] Gemini Generation failed: {e}")
        return f"<div class='p-10 bg-red-600 text-black font-bold'>GENERATION_ERROR: {topic}</div>"

def update_gallery(collage_html, topic):
    """File Persistence Logic. Correction: Aggressive Self-Healing and UTF-8 enforcement."""
    filepath = "index.html"
    marker = "<!-- GALLERY_INJECTION_POINT -->"
    
    # Template: Verified no Markdown links in the script tag
    base_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zaina Qureshi: Autonomic Archive</title>
    <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>
    <style>
        body {{ background-color: #f5f5f4; color: #000; font-family: 'Courier New', monospace; }}
        .brutalist-header {{ border-bottom: 4px solid #000; padding-bottom: 2rem; margin-bottom: 4rem; }}
        canvas {{ width: 100% !important; height: auto !important; display: block; }}
    </style>
</head>
<body class="p-4 md:p-12">
    <div class="max-w-5xl mx-auto">
        <header class="brutalist-header">
            <h1 class="text-6xl font-black uppercase tracking-tighter">Zaina Qureshi</h1>
            <p class="text-xl font-bold mt-2 text-red-600">Autonomic Digital Artist // Live Archive</p>
        </header>
        <div id="gallery">{marker}</div>
    </div>
</body>
</html>"""

    # Ensure index.html exists and is valid
    if not os.path.exists(filepath):
        print("[SYSTEM] index.html missing. Creating from template.")
        content = base_template
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if marker not in content:
            print("[SYSTEM] Marker missing. Forcing repair.")
            content = base_template

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    uid = int(time.time())
    
    new_entry = f"""
    <!-- ENTRY_START -->
    <div class="gallery-item mb-32 p-4 md:p-8 border-4 border-black bg-white shadow-[12px_12px_0px_rgba(217,48,37,1)]" id="art-{uid}">
        <div class="flex justify-between items-center mb-6 text-[10px] font-mono font-bold bg-black text-white p-3">
            <span>AUTONOMIC_STUDY // REF_{random.randint(10000, 99999)}</span>
            <span>{timestamp}</span>
        </div>
        <div class="relative w-full aspect-square md:aspect-video overflow-hidden border-2 border-black bg-white">
            {collage_html}
        </div>
        <div class="mt-6 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
            <div>
                <span class="text-[10px] bg-red-600 text-white px-2 py-0.5 font-bold uppercase">Subject</span>
                <h3 class="text-2xl font-black uppercase tracking-tighter mt-1">{topic}</h3>
            </div>
            <div class="text-[10px] text-right font-mono text-gray-500 uppercase leading-relaxed">
                Source: Scavenged_Web + Krea_Synthesis + Generative_JS<br>Status: Verified_Autonomic
            </div>
        </div>
    </div>
    <!-- ENTRY_END -->"""

    updated_content = content.replace(marker, marker + "\n" + new_entry)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(updated_content)
    print(f"[SUCCESS] File saved. Length: {len(updated_content)}")

if __name__ == "__main__":
    current_topic = random.choice(TOPICS)
    print(f"=== AWAKE: {current_topic} ===")
    art = generate_multimodal_collage(current_topic)
    update_gallery(art, current_topic)
