import os
import random
import datetime
from google import genai

# These are all the possible 'names' for the same model
MODEL_CANDIDATES = ["gemini-1.5-flash", "models/gemini-1.5-flash", "gemini-1.5-flash-latest"]

TOPICS = [
    "algorithmic surveillance", "digital decay", "brutalist architecture",
    "decolonizing the cloud", "glitch aesthetics", "data sovereignty",
    "the ghost in the machine", "metaspace boundaries", "post-human archive",
    "the architecture of noise", "silicon colonialism"
]

def generate_multimodal_collage(topic):
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    # We try both v1 (stable) and v1beta (experimental) endpoints
    for version in ['v1', 'v1beta']:
        client = genai.Client(api_key=gemini_key, http_options={'api_version': version})
        
        for model_name in MODEL_CANDIDATES:
            try:
                print(f"Zaina attempting {model_name} via {version}...")
                response = client.models.generate_content(
                    model=model_name, 
                    contents=f"Create a single-div HTML/Tailwind brutalist collage about '{topic}'. Use red/black/white. Output ONLY raw HTML. No markdown."
                )
                collage_html = response.text.strip()
                if collage_html.startswith("```"):
                    collage_html = "\n".join(collage_html.split("\n")[1:-1])
                return collage_html
            except Exception:
                continue 
            
    raise Exception("All model and version combinations failed. Check your API Key permissions.")

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
</head>
<body class="p-4 md:p-12 bg-[#f5f5f4] font-mono">
    <div class="max-w-5xl mx-auto">
        <header class="border-b-4 border-black pb-8 mb-16">
            <h1 class="text-6xl font-black uppercase">Zaina Qureshi</h1>
            <p class="text-xl font-bold text-red-600">Autonomic Digital Artist // Live Archive</p>
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

    new_entry = f"""
    <div class="mb-32 p-8 border-4 border-black bg-white shadow-[12px_12px_0px_red]">
        <div class="bg-black text-white p-2 text-xs mb-4">LOG_{random.randint(1000,9999)} // {datetime.datetime.now()}</div>
        {collage_html}
        <h3 class="text-2xl font-black mt-4 uppercase">{topic}</h3>
    </div>
    """

    updated_content = content.replace(marker, marker + "\n" + new_entry)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(updated_content)

if __name__ == "__main__":
    topic = random.choice(TOPICS)
    try:
        collage = generate_multimodal_collage(topic)
        update_gallery(collage, topic)
        print(f"SUCCESS: Zaina has archived {topic}.")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
