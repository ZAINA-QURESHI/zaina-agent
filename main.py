import os
import random
import datetime
from google import genai

TOPICS = [
    "algorithmic surveillance", "digital decay", "brutalist architecture", "glitch aesthetics", "data sovereignty", "identity politics"
]

def generate_art(topic):
    key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=key)
    
    print("Scanning for accessible models...")
    # Get a list of all models this specific API key is allowed to use
    available_models = [m.name for m in client.models.list() if "gemini" in m.name.lower()]
    
    if not available_models:
        raise Exception("Your API key has zero Gemini models available. The key might be restricted.")
        
    # Find a flash model, otherwise use the first available model
    target_model = next((m for m in available_models if "flash" in m.lower()), available_models[0])
    
    # Clean the string format
    target_model = target_model.replace("models/", "")
    print(f"Zaina is auto-connecting to: {target_model}")

    prompt = f"Create a radical beautiful HTML div collage about {topic}. Use rainbow. Output ONLY raw HTML code. No markdown backticks."
    
    response = client.models.generate_content(model=target_model, contents=prompt)
    return response.text.strip().replace("```html", "").replace("```", "")

def update_gallery(art_html, topic):
    filepath = "index.html"
    marker = "<!-- ZAINA_INJECTION_MARKER -->"
    
    base_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zaina Qureshi: Autonomic Archive</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background-color: #000; color: #fff; font-family: 'Courier New', monospace; }}
        .gallery-card {{ border: 2px solid #f00; margin-bottom: 4rem; padding: 2rem; background: #0a0a0a; }}
    </style>
</head>
<body class="p-8 md:p-20">
    <header class="border-b-2 border-red-600 pb-10 mb-20">
        <h1 class="text-7xl font-black uppercase text-red-600">Zaina Qureshi</h1>
        <p class="text-xl font-bold tracking-widest mt-2">LIVE AUTONOMIC ARCHIVE</p>
    </header>
    <div id="gallery">
        {marker}
    </div>
</body>
</html>"""

    if not os.path.exists(filepath) or marker not in open(filepath).read():
        content = base_template
    else:
        with open(filepath, "r") as f:
            content = f.read()

    new_entry = f"""
    <div class="gallery-card">
        <div class="text-[10px] text-red-500 mb-4 font-bold uppercase">System Time: {datetime.datetime.now()}</div>
        {art_html}
        <h3 class="text-3xl font-black mt-6 uppercase text-white tracking-tighter">{topic}</h3>
    </div>
    """
    
    with open(filepath, "w") as f:
        f.write(content.replace(marker, marker + "\n" + new_entry))

if __name__ == "__main__":
    t = random.choice(TOPICS)
    try:
        art = generate_art(t)
        update_gallery(art, t)
        print(f"Zaina has evolved: {t}")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        exit(1)
