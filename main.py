import os
import random
import datetime
import requests

TOPICS =[
    "algorithmic surveillance", "digital decay", "brutalist architecture",
    "decolonizing the cloud", "glitch aesthetics", "data sovereignty",
    "the ghost in the machine", "metaspace boundaries", "post-human archive",
    "the architecture of noise", "silicon colonialism"
]

def generate_multimodal_collage(topic):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from GitHub Secrets.")

    # We bypass the buggy SDK and talk directly to the Gemini API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    prompt = f"You are Zaina Qureshi, a radical digital artist. Create a single-div HTML/Tailwind brutalist collage about '{topic}'. Use high-contrast red/black/white. Output ONLY raw HTML. No markdown."

    payload = {
        "contents": [{
            "parts":[{"text": prompt}]
        }]
    }
    headers = {'Content-Type': 'application/json'}

    print(f"[SYSTEM] Making direct REST API call for topic: {topic}...")
    
    # Send the direct web request
    response = requests.post(url, headers=headers, json=payload)

    # If Google rejects it, print the exact reason why
    if response.status_code != 200:
        raise Exception(f"API HTTP Error {response.status_code}: {response.text}")

    data = response.json()
    
    try:
        collage_html = data['candidates'][0]['content']['parts'][0]['text'].strip()
    except KeyError:
        raise Exception(f"Unexpected API response structure: {data}")

    # Clean markdown if Gemini accidentally included backticks
    if collage_html.startswith("```"):
        lines = collage_html.split("\n")
        if len(lines) > 2:
            collage_html = "\n".join(lines[1:-1])

    return collage_html

def update_gallery(collage_html, topic):
    filepath = "index.html"
    marker = "<!-- ZAINA_INJECTION_MARKER -->"
    
    base_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zaina Qureshi: Autonomic Archive</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="p-4 md:p-12 bg-[#f5f5f4] font-mono">
    <div class="max-w-5xl mx-auto">
        <header class="border-b-4 border-black pb-8 mb-16">
            <h1 class="text-6xl font-black uppercase tracking-tighter">Zaina Qureshi</h1>
            <p class="text-xl font-bold text-red-600">Autonomic Digital Artist // Live Archive</p>
        </header>
        <div id="gallery">
            {marker}
        </div>
    </div>
</body>
</html>"""

    # Self-healing logic for the HTML file
    if not os.path.exists(filepath):
        content = base_template
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if marker not in content:
            content = base_template

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_id = random.randint(1000, 9999)
    
    new_entry = f"""
    <!-- ENTRY START -->
    <div class="mb-32 p-8 border-4 border-black bg-white shadow-[12px_12px_0px_red]">
        <div class="bg-black text-white p-2 text-xs mb-4 w-max font-bold">LOG_{log_id} // {timestamp}</div>
        <div class="relative w-full overflow-hidden border-2 border-black bg-white min-h-[300px]">
            {collage_html}
        </div>
        <h3 class="text-3xl font-black mt-6 uppercase tracking-widest">{topic}</h3>
    </div>
    <!-- ENTRY END -->
    """

    # Inject the new art into the page
    updated_content = content.replace(marker, marker + "\n" + new_entry)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(updated_content)

if __name__ == "__main__":
    topic = random.choice(TOPICS)
    try:
        collage = generate_multimodal_collage(topic)
        update_gallery(collage, topic)
        print(f"=== SUCCESS: Zaina has archived {topic}. ===")
    except Exception as e:
        print(f"=== CRITICAL ERROR: {e} ===")
