import os
import random
import datetime
from google import genai

# --- CONFIGURATION ---
# Removed 'models/' prefix as 'v1' often expects the direct string
MODEL_NAME = "gemini-1.5-flash"

TOPICS = [
    "algorithmic surveillance", "digital decay", "brutalist architecture",
    "decolonizing the cloud", "glitch aesthetics", "data sovereignty",
    "the ghost in the machine", "metaspace boundaries", "post-human archive",
    "the architecture of noise", "silicon colonialism"
]

def generate_multimodal_collage(topic):
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    # Explicitly using 'v1' to avoid the beta endpoint 404s
    client = genai.Client(
        api_key=gemini_key, 
        http_options={'api_version': 'v1'}
    )
    
    prompt = f"You are Zaina Qureshi, a radical digital artist. Create a single-div HTML/Tailwind brutalist collage about '{topic}'. Use high-contrast red/black/white. Output ONLY raw HTML. No markdown."
    
    response = client.models.generate_content(
        model=MODEL_NAME, 
        contents=prompt
    )
    
    collage_html = response.text.strip()
    if collage_html.startswith("```"):
        collage_html = "\n".join(collage_html.split("\n")[1:-1])
        
    return collage_html

def update_gallery(collage_html, topic):
    filepath = "index.html"
    marker = ""
    
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

    if not os.path.exists(filepath):
        content = base_template
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if marker not in content:
            content = base_template

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    uid = int(datetime.datetime.now().timestamp())
    
    new_entry = f"""
    <div class="gallery-item mb-32 p-4 md:p-8 border-4 border-black bg-white shadow-[12px_12px_0px_rgba(217,48,37,1)]" id="art-{uid}">
        <div class="flex justify-between items-center mb-6 text-[10px] font-mono font-bold bg-black text-white p-3">
            <span>AUTONOMIC_STUDY // REF_{random.randint(10000, 99999)}</span>
            <span>{timestamp}</span>
        </div>
        <div class="relative w-full overflow-hidden border-2 border-black bg-white min-h-[300px]">
            {collage_html}
        </div>
        <div class="mt-6">
            <h3 class="text-2xl font-black uppercase tracking-tighter">{topic}</h3>
        </div>
    </div>
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
        print("=== PUBLISH SUCCESSFUL ===")
    except Exception as e:
        print(f"=== CRITICAL ERROR: {e} ===")
