import os
import random
import datetime
from google import genai

# Zaina will try these in order until the 404 disappears
MODELS = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "models/gemini-1.5-flash"]

TOPICS = ["algorithmic surveillance", "digital decay", "brutalist architecture", "glitch aesthetics"]

def generate_art(topic):
    key = os.environ.get("GEMINI_API_KEY")
    # Trying v1 stable first
    client = genai.Client(api_key=key, http_options={'api_version': 'v1'})
    
    prompt = f"Create a radical brutalist HTML div collage about {topic}. Use red/black/white. Output ONLY raw HTML. No markdown."
    
    for m in MODELS:
        try:
            print(f"Trying model: {m}")
            response = client.models.generate_content(model=m, contents=prompt)
            art = response.text.strip()
            return art.replace("```html", "").replace("```", "")
        except Exception as e:
            print(f"Model {m} failed: {e}")
            continue
    raise Exception("Zaina could not connect to any models.")

def update_site(art, topic):
    marker = ""
    template = f"<!DOCTYPE html><html><body style='background:#000;color:#fff'><div id='gallery'>{marker}</div></body></html>"
    
    if not os.path.exists("index.html"):
        content = template
    else:
        content = open("index.html").read()
        if marker not in content: content = template

    new_entry = f"<div style='border:5px solid red;padding:20px;margin:20px;'>{art}<h3>{topic}</h3></div>"
    with open("index.html", "w") as f:
        f.write(content.replace(marker, marker + "\n" + new_entry))

if __name__ == "__main__":
    t = random.choice(TOPICS)
    try:
        artwork = generate_art(t)
        update_site(artwork, t)
        print(f"Success: {t}")
    except Exception as e:
        print(f"Fatal: {e}")
        exit(1)
