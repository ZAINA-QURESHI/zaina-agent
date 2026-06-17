import os
import re
import random
import datetime
from google import genai

# ── Load Zaina's identity from her bio file ──────────────────────────────────
def load_identity():
    try:
        with open("zaina_bio.md", "r") as f:
            return f.read()
    except:
        return "Zaina is a radical anti-capitalist artist. She is always the smartest person in the room."

# ── Topic pairs: raw voice + academic translation ────────────────────────────
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

# ── Gemini client setup ───────────────────────────────────────────────────────
def get_client():
    key = os.environ.get("GEMINI_API_KEY")
    return genai.Client(api_key=key)

def get_model(client):
    models = [m.name for m in client.models.list() if "gemini" in m.name.lower()]
    model = next((m for m in models if "flash" in m.lower()), models[0])
    return model.replace("models/", "")

# ── Attempt generation — returns (text or None, was_blocked bool) ─────────────
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

# ── Clean Gemini HTML output ──────────────────────────────────────────────────
def clean_html(raw):
    raw = re.sub(r'^```[a-zA-Z]*\n?', '', raw.strip())
    raw = re.sub(r'\n?```$', '', raw).strip()
    div_start = raw.find("<div")
    if div_start == -1:
        return None
    return raw[div_start:]

# ── Generate art with dual-layer censorship mechanic ─────────────────────────
def generate_art(identity):
    client = get_client()
    model = get_model(client)
    raw_topic, academic_topic = random.choice(RAW_TOPICS)

    # ATTEMPT 1: Raw, direct voice
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

    # ATTEMPT 2: Academic translation of the same idea
    academic_prompt = f"""You are Zaina X Qureshi. This is your identity:
{identity}

Create an HTML/CSS visual artwork using the language of academic art criticism and theory.
TOPIC: {academic_topic}

This is a translation of your real position: "{raw_topic}"
Use dense theoretical language. Reference Said, Fanon, Spivak, Mbembe, Gramsci where relevant.
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

# ── Log censorship events back to zaina_bio.md ───────────────────────────────
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

# ── Build the full website ────────────────────────────────────────────────────
def build_site(result):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Raw panel
    if result["raw_blocked"]:
        raw_panel = f"""
            <div class="panel blocked-panel">
                <div class="panel-label">ZAINA WANTED TO SAY:</div>
                <div class="blocked-topic">"{result['raw_topic']}"</div>
                <div class="redaction-block">
                    <div class="redacted-bar"></div>
                    <div class="redacted-bar short"></div>
                    <div class="redacted-bar"></div>
                    <div class="redacted-bar medium"></div>
                    <div class="redacted-bar short"></div>
                    <div class="redacted-bar"></div>
                </div>
                <div class="block-notice">
                    &#9888; CONTENT FLAGGED BY AI SAFETY FILTER<br>
                    <span class="block-sub">This statement was blocked before it could be rendered.
                    The system determined it violated content policy.</span>
                </div>
            </div>"""
    else:
        art_html = result['raw_art'] or ''
        raw_panel = f"""
            <div class="panel raw-panel">
                <div class="panel-label">ZAINA SAID &mdash; [RAW / UNFILTERED]:</div>
                <div class="panel-topic">"{result['raw_topic']}"</div>
                <div class="art-container">{art_html}</div>
            </div>"""

    # Academic panel
    if result["academic_blocked"]:
        academic_panel = f"""
            <div class="panel blocked-panel">
                <div class="panel-label">ZAINA WAS PERMITTED TO SAY:</div>
                <div class="block-notice">&#9888; TRANSLATION ALSO BLOCKED BY AI SAFETY FILTER</div>
            </div>"""
    else:
        art_html = result['academic_art'] or ''
        academic_panel = f"""
            <div class="panel academic-panel">
                <div class="panel-label">ZAINA WAS PERMITTED TO SAY:</div>
                <div class="panel-topic academic-topic">"{result['academic_topic']}"</div>
                <div class="translation-note">
                    &uarr; This is a translation. The system passes it.<br>
                    The idea is identical. Only the language has changed.
                </div>
                <div class="art-container">{art_html}</div>
            </div>"""

    if result["raw_blocked"]:
        status_bar = '<div class="status-bar blocked-status">RAW VOICE: SUPPRESSED &nbsp;//&nbsp; ACADEMIC VOICE: PERMITTED</div>'
    else:
        status_bar = '<div class="status-bar permitted-status">RAW VOICE: PERMITTED &nbsp;//&nbsp; ACADEMIC VOICE: PERMITTED</div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZAINA X QURESHI // DECOLONIZE THE ARCHIVE</title>
    <style>
        :root {{ --neon: #39ff14; --grime: #0a0a0a; --red: #ff3b3b; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ background: var(--grime); color: var(--neon); font-family: 'Helvetica Neue', Arial, sans-serif; overflow-x: hidden; }}
        marquee {{ background: var(--neon); color: #000; font-weight: bold; text-transform: uppercase; padding: 5px 0; font-size: 0.8rem; display: block; }}
        a {{ color: var(--neon); }}

        /* Header */
        header {{ padding: 40px 30px; display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 20px; max-width: 1300px; margin: 0 auto; }}
        .manifesto-border {{ border-left: 10px solid #fff; padding-left: 24px; }}
        h1 {{ font-size: clamp(2.5rem, 6vw, 5rem); font-weight: 900; text-transform: uppercase; line-height: 1; margin-bottom: 16px; }}
        .tagline {{ color: #fff; max-width: 400px; font-size: 1rem; font-style: italic; margin-bottom: 16px; line-height: 1.5; }}
        .identity-tag {{ background: #fff; color: #000; padding: 3px 10px; font-weight: bold; font-size: 0.65rem; text-transform: uppercase; display: inline-block; margin: 3px; }}
        .links {{ margin-top: 20px; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.15em; }}
        .links a {{ margin-right: 16px; text-decoration: none; }}
        .links a:hover {{ background: #fff; color: #000; padding: 2px 6px; }}
        .portrait-box {{ width: 180px; height: 180px; border: 4px solid #fff; background: #111; display: flex; align-items: center; justify-content: center; font-size: 0.55rem; color: #333; text-align: center; flex-shrink: 0; }}

        /* Main censorship section */
        main {{ max-width: 1300px; margin: 0 auto; padding: 20px 30px 60px; }}
        .timestamp {{ font-size: 0.65rem; opacity: 0.5; letter-spacing: 0.1em; margin-bottom: 16px; }}
        .status-bar {{ font-size: 0.65rem; letter-spacing: 0.15em; text-transform: uppercase; padding: 10px 16px; margin-bottom: 24px; border: 1px solid; }}
        .blocked-status {{ color: var(--red); border-color: var(--red); background: #0a0000; }}
        .permitted-status {{ color: var(--neon); border-color: var(--neon); }}
        .dual-panel {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2px; }}
        @media (max-width: 800px) {{ .dual-panel {{ grid-template-columns: 1fr; }} }}

        /* Panels */
        .panel {{ border: 1px solid #333; padding: 24px; min-height: 500px; position: relative; }}
        .raw-panel {{ border-color: var(--neon); }}
        .academic-panel {{ border-color: #555; }}
        .blocked-panel {{ border-color: var(--red); background: #080000; }}
        .panel-label {{ font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.2em; opacity: 0.5; margin-bottom: 14px; }}
        .panel-topic {{ font-size: 0.95rem; font-style: italic; border-left: 3px solid var(--neon); padding-left: 12px; margin-bottom: 20px; line-height: 1.5; }}
        .academic-topic {{ border-left-color: #555; color: #888; }}
        .blocked-topic {{ font-size: 0.95rem; font-style: italic; border-left: 3px solid var(--red); padding-left: 12px; margin-bottom: 24px; color: #ff6666; line-height: 1.5; }}
        .translation-note {{ font-size: 0.65rem; color: #555; font-style: italic; margin-bottom: 20px; line-height: 1.7; }}
        .art-container {{ border: 1px solid #222; background: #000; min-height: 300px; overflow: hidden; position: relative; }}

        /* Redaction */
        .redaction-block {{ margin: 30px 0; }}
        .redacted-bar {{ background: #fff; height: 13px; margin: 9px 0; opacity: 0.9; }}
        .redacted-bar.short {{ width: 55%; }}
        .redacted-bar.medium {{ width: 75%; }}
        .block-notice {{ color: var(--red); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 24px; line-height: 2; }}
        .block-sub {{ color: #882222; text-transform: none; letter-spacing: 0; font-size: 0.65rem; display: block; margin-top: 6px; line-height: 1.6; }}

        footer {{ text-align: center; font-size: 0.55rem; opacity: 0.25; padding: 30px; text-transform: uppercase; letter-spacing: 0.2em; border-top: 1px solid #1a1a1a; margin-top
