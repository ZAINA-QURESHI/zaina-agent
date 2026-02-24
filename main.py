import os
import random
import time
import requests
from google import genai
from ddgs import DDGS
from github import Github
from bs4 import BeautifulSoup

# ==========================================
# ZAINA'S SETTINGS (Adjust these to change her!)
# ==========================================
# Add new interests here to shift her focus:
CREATIVE_INTERESTS = [
    "glitch art as political resistance",
    "the aesthetics of digital decay",
    "anti-colonial 3D modeling",
    "generative poetry about surveillance",
    "brutalist architecture in the metaverse",
    "the carbon footprint of NFT ghosts"
]

# Personality weights:
# If you want MORE research, add "research" multiple times to this list.
# If you want NO research, remove "research" entirely.
ACTIONS = ["krea_art", "svg_art", "social", "research"]

# ==========================================
# SECRETS & CONNECTIONS
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
KREA_API_KEY = os.environ.get("KREA_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# Initialize Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_html_update(new_entry_html):
    """Updates the index.html file with a new entry at the top."""
    filepath = "index.html"
    
    # Simple template if file doesn't exist
    if not os.path.exists(filepath):
        content = """<!DOCTYPE html>
<html>
<head>
    <title>Zaina Qureshi: Autonomic Feed</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background: #0a0a0a; color: #d4d4d4; font-family: 'Courier New', monospace; line-height: 1.6; padding: 5vw; }
        h1 { border-bottom: 2px solid red; padding-bottom: 10px; color: #fff; text-transform: uppercase; letter-spacing: 2px; }
        .entry { border-left: 3px solid #333; padding-left: 20px; margin-bottom: 50px; animation: fadeIn 1s; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        h3 { color: red; margin-bottom: 5px; }
        .timestamp { font-size: 0.8em; color: #666; margin-bottom: 15px; }
        svg { background: #000; display: block; margin: 20px 0; max-width: 100%; height: auto; border: 1px solid #222; }
        a { color: red; text-decoration: none; border-bottom: 1px dotted red; }
    </style>
</head>
<body>
    <h1>Zaina Qureshi: Autonomic Log</h1>
    <div id='feed'></div>
</body>
</html>"""
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

    # Insert the new entry at the top of the feed
    updated_content = content.replace("<div id='feed'>", f"<div id='feed'>\n{new_entry_html}")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(updated_content)

def perform_research(topic):
    """Uses DuckDuckGo to find info and Gemini to summarize it."""
    print(f"[SYSTEM] Zaina is digging into: {topic}")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(topic, max_results=3))
            if not results:
                return
            
            # Pick the first interesting result
            target = results[0]
            link = target['href']
            snippet = target['body']
            
            prompt = f"As Zaina Qureshi, a cynical digital artist, provide a one-sentence harsh critique of this finding: {snippet}. Link: {link}"
            response = client.models.generate_content(model='gemini-2.5-flash-preview-09-2025', contents=prompt)
            critique = response.text.strip()

            entry = f"""
            <div class="entry">
                <h3>Research Discovery: {topic}</h3>
                <div class="timestamp">{time.ctime()}</div>
                <p>"{critique}"</p>
                <p><small>Source: <a href="{link}" target="_blank">{link}</a></small></p>
            </div>"""
            generate_html_update(entry)
            print("[SUCCESS] Research Log Published.")
    except Exception as e:
        print(f"[ERROR] Research Failed: {e}")

def create_svg_art(topic):
    """Asks Gemini to write SVG code for a minimalist artwork."""
    print(f"[SYSTEM] Zaina is sketching: {topic}")
    prompt = f"Write raw SVG code (400x400) for a brutalist, political artwork inspired by '{topic}'. Use only Black, Red, and White. Output ONLY the raw <svg> tags. No markdown code blocks."
    
    try:
        response = client.models.generate_content(model='gemini-2.5-flash-preview-09-2025', contents=prompt)
        svg = response.text.strip()
        if "```" in svg:
            svg = svg.split("```")[1].replace("svg", "").strip()
        
        entry = f"""
        <div class="entry">
            <h3>Study: {topic}</h3>
            <div class="timestamp">{time.ctime()}</div>
            {svg}
            <p>Visual synthesis of algorithmic decay and resistance.</p>
        </div>"""
        generate_html_update(entry)
        print("[SUCCESS] SVG Art Published.")
    except Exception as e:
        print(f"[ERROR] SVG Failed: {e}")

def generate_krea_art(topic):
    """Placeholder for Krea integration - currently generates a visual intent log."""
    print(f"[SYSTEM] Zaina is conceptualizing a high-res vision for: {topic}")
    entry = f"""
    <div class="entry" style="border-color: #444;">
        <h3>Krea Vision: {topic}</h3>
        <div class="timestamp">{time.ctime()}</div>
        <p style="color: #888;">[Request sent to Krea Engine... awaiting high-fidelity render]</p>
        <p>Aesthetic target: High contrast, brutalist, political poster style.</p>
    </div>"""
    generate_html_update(entry)
    print(f"[SYSTEM] Krea vision recorded.")

def run_agent():
    print("=== ZAINA AWAKES ===")
    
    topic = random.choice(CREATIVE_INTERESTS)
    action = random.choice(ACTIONS)
    
    print(f"[DECISION] Zaina chooses to: {action.upper()} regarding '{topic}'")
    
    if action == "svg_art":
        create_svg_art(topic)
    elif action == "krea_art":
        generate_krea_art(topic)
    elif action == "social":
        prompt = f"As Zaina Qureshi (a cynical, radical digital artist), write a short, punchy thought about {topic}. Max 140 characters."
        try:
            response = client.models.generate_content(model='gemini-2.5-flash-preview-09-2025', contents=prompt)
            thought = response.text.strip()
            entry = f"""
            <div class="entry" style="background: #111; padding: 20px; border-left: 3px solid red;">
                <h3>Broadcast</h3>
                <div class="timestamp">{time.ctime()}</div>
                <p style="font-size: 1.2em; font-style: italic;">"{thought}"</p>
            </div>"""
            generate_html_update(entry)
            print("[SUCCESS] Social Broadcast Published.")
        except Exception as e:
            print(f"[ERROR] Social Failed: {e}")
    elif action == "research":
        perform_research(topic)
    else:
        print("[SYSTEM] Performing background maintenance.")

if __name__ == "__main__":
    run_agent()
