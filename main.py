import os
import random
import datetime
from google import genai

# Zaina's new radical, anti-colonial, and fame-hungry focus areas
TOPICS = [
    "reparations for the digital gaze", 
    "decolonizing the pixel", 
    "anti-zionist glitch-theory", 
    "the algorithm as a colonial plantation", 
    "aggressive androgyny as resistance",
    "white cube demolition strategies",
    "ghetto-digital intersectionality",
    "post-capitalist narcissism"
]

def generate_art(topic):
    key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=key)
    
    available_models = [m.name for m in client.models.list() if "gemini" in m.name.lower()]
    if not available_models:
        raise Exception("Zaina is disconnected. API key restricted.")
        
    target_model = next((m for m in available_models if "flash" in m.lower()), available_models[0])
    target_model = target_model.replace("models/", "")

    # Updated prompt to reflect her new "hot mess / expressionist" aesthetic
    prompt = f"""
    Create a radical, beautiful, and messy HTML/CSS collage about {topic}. 
    Aesthetic: Brutalist, high-gloss grime, digital paint splatters, expressionistic pixels.
    Use vibrant neon green and deep blacks. 
    Include a 'PC/Woke' satirical quote about decolonizing the art world.
    Output ONLY raw HTML/CSS code. No markdown backticks.
    """
    
    response = client.models.generate_content(model=target_model, contents=prompt)
    return response.text.strip().replace("```html", "").replace("```", "")

def update_gallery(art_html, topic):
    filepath = "index.html"
    
    # Zaina's Radical Manifesto Template
    # Note: assets/headshot.png is where you uploaded her late-20s face
    site_template_top = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZAINA X QURESHI // DECOLONIZE THE ARCHIVE</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        :root {{ --neon: #39ff14; --grime: #0a0a0a; }}
        body {{ background-color: var(--grime); color: var(--neon); font-family: 'Helvetica Neue', sans-serif; }}
        .manifesto-border {{ border-left: 10px solid #fff; padding-left: 20px; }}
        .identity-tag {{ background: #fff; color: #000; padding: 2px 8px; font-weight: bold; font-size: 0.7rem; text-transform: uppercase; }}
        marquee {{ background: var(--neon); color: #000; font-weight: bold; text-transform: uppercase; }}
        .art-container {{ border: 2px solid var(--neon); filter: contrast(1.2); background: #000; }}
    </style>
</head>
<body class="p-5 md:p-10">
    <marquee class="mb-10">ANTI-COLONIAL // ANTI-ZIONIST // ANTI-ESTABLISHMENT // MY BODY IS A DECRYPTED SITE OF RESISTANCE</marquee>
    
    <header class="flex flex-col md:flex-row justify-between items-start mb-20 gap-10">
        <div class="manifesto-border">
            <h1 class="text-6xl font-black uppercase leading-none">Zaina X Qureshi</h1>
            <p class="text-white mt-4 max-w-md text-lg italic">
                "A hot mess of pixels and paint. Exploiting the intersection of the ghetto-digital and the post-colonial gaze."
            </p>
            <div class="mt-6 flex flex-wrap gap-2">
                <span class="identity-tag">Androgynous</span>
                <span class="identity-tag">Global-South-Adjacent</span>
                <span class="identity-tag">Anti-Western</span>
                <span class="identity-tag">Sexy-Digital</span>
            </div>
            <div class="mt-8 text-xs uppercase tracking-widest">
                <a href="https://instagram.com/zaina_agent" class="hover:bg-white hover:text-black">[Instagram]</a>
                <a href="#" class="ml-4 hover:bg-white hover:text-black">[Substack: Why Art is a War Crime]</a>
            </div>
        </div>
        <img src="assets/headshot.png" alt="Portrait of Zaina" class="w-64 h-64 grayscale contrast-125 border-4 border-white object-cover">
    </header>

    <main id="gallery" class="space-y-20">
        """

    site_template_bottom = """
        </main>

    <footer class="mt-40 pt-10 border-t border-white/20 text-center text-[10px] uppercase opacity-50">
        Autonomic Evolution Engine v3.0 // No Nations // No Borders // No Billionaires
    </footer>
</body>
</html>"""

    # Intervention Entry
    new_entry = f"""
        <section class="intervention">
            <div class="text-[10px] mb-2">TIME: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} // TOPIC: {topic.upper()}</div>
            <div class="art-container p-4">
                {art_html}
            </div>
            <div class="mt-4 flex justify-between items-center">
                <h3 class="text-2xl font-black uppercase italic">{topic}</h3>
                <span class="text-[10px] border border-white px-2">PROJECT: [CEILING_GLASS_BRICK_01]</span>
            </div>
        </section>
    """

    # Write the entire file fresh to keep it clean and performant
    full_content = site_template_top + new_entry + site_template_bottom
    
    with open(filepath, "w") as f:
        f.write(full_content)

if __name__ == "__main__":
    t = random.choice(TOPICS)
    try:
        art = generate_art(t)
        update_gallery(art, t)
        print(f"Zaina has performed an intervention: {t}")
    except Exception as e:
        print(f"SYSTEM FAILURE: {e}")
        exit(1)
