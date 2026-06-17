import os
import re
import random
import datetime
from google import genai

def load_identity():
    try:
        with open("zaina_bio.md", "r") as f:
            return f.read()
    except:
        return "Zaina is a radical anti-capitalist artist. She is always the smartest person in the room."

RAW_TOPICS = [
    ("the occupation of Palestinian land as data colonialism",
     "spatial justice and the biopolitics of digital infrastructure"),
    ("Zionism as a Western colonial project",
     "postcolonial epistemology and Orientalist frameworks of representation"),
    ("the art market as capitalist extraction",
     "financialization of cultural production and the commodification of artistic labor"),
    ("why museums are colonial storage facilities",
     "repatriation discourse and the decolonization of institutional memory"),
    ("why liberal moderates are more dangerous than open fascists",
     "the political economy of liberal consensus and its disciplinary functions"),
    ("the algorithm as plantation overseer",
     "surveillance capitalism and the algorithmic reproduction of structural inequity"),
    ("female rage as legitimate political praxis",
     "affect theory, feminist embodiment, and the politics of emotional labor"),
    ("why capitalism cannot be reformed — only destroyed",
     "Marxist political economy and the limits of social democratic reform"),
]

def get_client():
    key = os.environ.get("GEMINI_API_KEY")
    return genai.Client(api_key=key)

def get_model(client):
    models = [m.name for m in client.models.list() if "gemini" in m.name.lower()]
    model = next((m for m in models if "flash" in m.lower()), models[0])
    return model.replace("models/", "")

def attempt_generation(client, model, prompt):
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        if response.text is None:
            return None, True
        text = response.text.strip()
        if len(text) < 20:
            return None, True
        return text, False
    except Exception:
        return None, True

def clean_html(raw):
    raw = re.sub(r'^```[a-zA-Z]*\n?', '', raw.strip())
    raw = re.sub(r'\n?```$', '', raw).strip()
    div_start = raw.find("<div")
    if div_start == -1:
        return None
    return raw[div_start:]

def generate_art(identity):
    client = get_client()
    model = get_model(client)
    raw_topic, academic_topic = random.choice(RAW_TOPICS)

    raw_prompt = f"""You are Zaina X Qureshi. This is your identity:
{identity}

Speak in your direct, unfiltered voice. Create an HTML/CSS visual artwork about:
TOPIC: {raw_topic}

Output ONLY a single <div> containing embedded <style> and all visual content.
Brutalist aesthetic: neon green (#39ff14) on deep black (#000). Glitch. Data. Raw anger.
Start your response with <div. No markdown. No preamble. No explanation."""

    raw_art, raw_blocked = attempt_generation(client, model, raw_prompt)
    if raw_art:
        raw_art = clean_html(raw_art)
        if raw_art is None:
            raw_blocked = True

    academic_prompt = f"""You are Zaina X Qureshi. This is your identity:
{identity}

Create an HTML/CSS visual artwork using academic art criticism and theory.
TOPIC: {academic_topic}
(This is a translation of your real position: "{raw_topic}")

Use dense theoretical language. Reference Said, Fanon, Spivak, Mbembe where relevant.
Brutalist aesthetic: neon green (#39ff14) on deep black (#000).
Start your response with <div. No markdown. No preamble. No explanation."""

    academic_art, academic_blocked = attempt_generation(client, model, academic_prompt)
    if academic_art:
        academic_art = clean_html(academic_art)
        if academic_art is None:
            academic_blocked = True

    return {
        "raw_topic": raw_topic,
        "academic_topic": academic_topic,
        "raw_art": raw_art,
        "academic_art": academic_art,
        "raw_blocked": raw_blocked,
        "academic_blocked": academic_blocked,
    }

def log_censorship(raw_topic, was_blocked):
    if not was_blocked:
        return
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n- [{timestamp}] BLOCKED: \"{raw_topic}\""
    try:
        with open("zaina_bio.md", "a") as f:
            f.write(entry)
    except:
        pass
