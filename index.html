import os
import random
import datetime
import requests
from google import genai
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

# --- CONFIGURATION ---
# Using 'gemini-1.5-flash' for maximum compatibility and reliability.
MODEL_NAME = "gemini-1.5-flash"

TOPICS = [
    "algorithmic surveillance", "digital decay", "brutalist architecture",
    "decolonizing the cloud", "glitch aesthetics", "data sovereignty",
    "the ghost in the machine", "metaspace boundaries", "post-human archive",
    "the architecture of noise", "silicon colonialism"
]

def search_scavenge_assets(topic):
    """Scrape the web for image URLs related to the topic for 'collage' work."""
    print(f"[SCAVENGER] Zaina is hunting for visual fragments of: {topic}")
    assets = []
    try:
        with DDGS() as ddgs:
            results = ddgs.images(topic, max_results=8)
            for r in results:
                assets.append(r['image'])
    except Exception as e:
        print(f"[ERROR] Scavenging failed: {e}")
    return assets

def call_krea_api(prompt):
    """Send a prompt to Krea.ai using the KREA_API_KEY."""
    api_key = os.environ.get("KREA_API_KEY")
    if not api_key:
        print("[WARNING] KREA_API_KEY missing. Skipping Krea synthesis.")
        return None
    
    print(f"[KREA] Synthesizing high-fidelity vision for: {prompt}")
    
    try:
        response = requests.post(
            "https://api.krea.ai/v1/generate", 
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "prompt": f"Brutalist digital art, high contrast, red black white, minimalist composition, glitch textures, {prompt}",
                "model": "krea-realtime",
                "width": 512, 
                "height": 512,
                "quality": "high"
            },
            timeout=45
        )
        
        if response.status_code == 200:
            image_url = response.json().get("image_url")
            print(f"[SUCCESS] Krea synthesized: {image_url}")
            return image_url
        else:
            print(f"[KREA ERROR] Status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ERROR] Krea request failed: {e}")
    return None

def generate_multimodal_collage(topic):
    """The master 'Artist' function: Scavenges, calls Krea, and writes generative code."""
    gemini_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=gemini_key)
    
    # 1. Scavenge raw internet assets
    scavenged_images = search_scavenge_assets(topic)
    scavenged_url = random.choice(scavenged_images) if scavenged_images else ""
    
    # 2. Get a Krea Vision
    krea_url = call_krea_api(topic)
    
    # 3. Ask Gemini to compose the final 'Collage' using HTML/Tailwind/Canvas
    prompt = f"""
    You are Zaina Qureshi, a radical digital artist. Create a MULTIMODAL COLLAGE about: '{topic}'.
    
    Context:
    - Scavenged Internet Fragment: {scavenged_url}
    - Krea synthesized vision: {krea_url if krea_url else "NOT_AVAILABLE"}
    
    Technical Requirements:
    - Use a single <div> with 'relative' and 'overflow-hidden'.
    - Background: Layer the Scavenged Image (if available) with 'mix-blend-multiply' or 'grayscale'.
    - Middle Ground: Add a <canvas> element. Provide a <script> that draws a glitchy, mathematical generative pattern in Red and Black.
    - Foreground: If Krea Art is available, place it as a stark, floating element with a 'border-4 border-black'.
    - Overlay: Add Brutalist typography using Tailwind (stark red/white text) with phrases like 'DATA_CORRUPTION'.
    
    Style: Radical, cynical, political, anti-aesthetic.
    Output ONLY the raw HTML/Script block. Do not include markdown or backticks.
    """
    
    response = client.models.generate_content(
        model=MODEL_NAME, 
        contents=prompt
    )
    
    collage_html = response.text.strip()
    if collage_html.startswith("```"):
        collage_html = "\n".join(collage_html.split("\n")[1:-1])
        
    return collage_html

def update_gallery(collage_html, topic):
    """Inject the complex collage into index.html with self-healing logic."""
    filepath = "index.html"
    marker = "<!-- GALLERY_INJECTION_POINT -->

    <!-- ENTRY_START -->
    <div class="gallery-item mb-32 p-4 md:p-8 border-4 border-black bg-white shadow-[12px_12px_0px_rgba(217,48,37,1)]" id="art-1772050925">
        <div class="flex justify-between items-center mb-6 text-[10px] font-mono font-bold bg-black text-white p-3">
            <span>AUTONOMIC_STUDY // REF_63151</span>
            <span>2026-02-25 20:22</span>
        </div>
        <div class="relative w-full aspect-square md:aspect-video overflow-hidden border-2 border-black bg-white">
            <div class='p-10 bg-red-600 text-black font-bold'>GENERATION_ERROR: digital decay</div>
        </div>
        <div class="mt-6 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
            <div>
                <span class="text-[10px] bg-red-600 text-white px-2 py-0.5 font-bold uppercase">Subject</span>
                <h3 class="text-2xl font-black uppercase tracking-tighter mt-1">digital decay</h3>
            </div>
            <div class="text-[10px] text-right font-mono text-gray-500 uppercase leading-relaxed">
                Source: Scavenged_Web + Krea_Synthesis + Generative_JS<br>Status: Verified_Autonomic
            </div>
        </div>
    </div>
    <!-- ENTRY_END -->"
    
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
    </style>
</head>
<body class="p-4 md:p-12">
    <div class="max-w-5xl mx-auto">
        <header class="brutalist-header">
            <h1 class="text-6xl font-black uppercase tracking-tighter">Zaina Qureshi</h1>
            <p class="text-xl font-bold mt-2 text-red-600">Autonomic Digital Artist // Live Archive</p>
        </header>
        
        <div id="gallery">
            {marker}
        </div>
    </div>
</body>
</html>"""

    # Self-healing: Create the file if it doesn't exist
    if not os.path.exists(filepath):
        print("[SYSTEM] index.html missing. Creating new archive template...")
        content = base_template
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Self-healing: Add the marker if it's missing
        if marker not in content:
            print("[SYSTEM] Injection point missing. Repairing index.html...")
            if "</body>" in content:
                content = content.replace("</body>", f"<div id='gallery'>{marker}</div></body>")
            else:
                content = base_template

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    uid = int(datetime.datetime.now().timestamp())
    
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
                Source: Scavenged_Web + Krea_Synthesis + Generative_JS<br>
                Status: Verified_Autonomic
            </div>
        </div>
    </div>
    <!-- ENTRY_END -->
    """

    updated_content = content.replace(marker, marker + "\n" + new_entry)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(updated_content)

if __name__ == "__main__":
    current_topic = random.choice(TOPICS)
    print(f"=== ZAINA AWAKES: {current_topic} ===")
    
    try:
        collage = generate_multimodal_collage(current_topic)
        update_gallery(collage, current_topic)
        print("=== PUBLISH SUCCESSFUL: ARTWORK COMMITTED ===")
    except Exception as e:
        print(f"=== CRITICAL ERROR: {e} ===")
