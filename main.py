import os
import random
import datetime
import requests
from google import genai
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

# --- CONFIGURATION ---
# We are using 'gemini-1.5-flash' for stability and speed.
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
        print("[WARNING] KREA_API_KEY missing in environment. Skipping Krea synthesis.")
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
    """Inject the complex collage into index.html."""
    if not os.path.exists("index.html"):
        print("[ERROR] index.html not found.")
        return

    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    uid = int(datetime.datetime.now().timestamp())
    
    new_entry = f"""
    <!-- ENTRY_START -->
    <div class="gallery-item mb-32 p-4 md:p-8 border-4 border-black bg-stone-100 shadow-[12px_12px_0px_rgba(217,48,37,1)]" id="art-{uid}">
        <div class="flex justify-between items-center mb-6 text-[10px] font-mono font-bold bg-black text-white p-3">
            <span>AUTONOMIC_STUDY // REF_{random.randint(10000, 99999)}</span>
            <span>{timestamp}</span>
        </div>
        <div class="relative w-full aspect-square md:aspect-video overflow-hidden border-2 border-black bg-white group">
            {collage_html}
            <div class="absolute inset-0 border-[20px] border-black opacity-10 pointer-events-none"></div>
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

    marker = "<!-- GALLERY_INJECTION_POINT -->"
    if marker not in content:
        print("[ERROR] Injection point comment missing in index.html")
        return

    updated_content = content.replace(marker, marker + "\n" + new_entry)

    with open("index.html", "w", encoding="utf-8") as f:
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
