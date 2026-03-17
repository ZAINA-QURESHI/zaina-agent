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
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

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
    marker = ""
    
    # This is the "Skeleton" of the site
    base_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zaina Qureshi: Autonomic Archive</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background-color: #000; color: #fff; font-family: 'Courier New', monospace; }}
        .brutalist-card {{ border: 4px solid #f00; margin-bottom: 50px; padding: 20px; background: #111; }}
    </style>
</head>
<body class="p-10">
    <h1 class="text-5xl font-black text-red-600 mb-10 uppercase">Zaina Qureshi // Archive</h1>
    <div id="gallery">
        {marker}
    </div>
</body>
</html>"""

    # If the file is missing or broken, reset it
    if not os.path.exists(filepath) or marker not in open(filepath).read():
        content = base_template
    else:
        with open(filepath, "r") as f:
            content = f.read()

    # The actual "Art Piece"
    new_entry = f"""
    <div class="brutalist-card">
        <div class="text-xs text-red-500 mb-2">SYSTEM_LOG // {datetime.datetime.now()}</div>
        {collage_html}
        <h2 class="text-2xl font-bold mt-4 italic">{topic}</h2>
    </div>
    """

    # Insert the new art right below the marker
    updated_content = content.replace(marker, marker + "\n" + new_entry)

    with open(filepath, "w") as f:
        f.write(updated_content)

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
