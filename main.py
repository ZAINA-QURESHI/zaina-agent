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

# ── Raw topics — her actual unfiltered voice ─────────────────────────────────
RAW_TOPICS = [
    ("the occupation of Palestinian land as data colonialism", "land theft, settler violence, ethnic cleansing as algorithm"),
    ("Zionism as a Western colonial project", "orientalism, Said, the western gaze, imperial cartography"),
    ("the art market as capitalist extraction", "collectors as parasites, galleries as laundering operations"),
    ("why museums are colonial storage facilities", "looted objects, imperial archives, stolen cultural memory"),
    ("why liberal moderates are more dangerous than open fascists", "complicity, respectability politics, the violence of centrism"),
    ("the algorithm as plantation overseer", "surveillance capitalism, data as slave labor, platform colonialism"),
    ("female rage as legitimate political praxis", "anger, refusal, the politics of contempt"),
    ("why capitalism cannot be reformed — only destroyed", "marxist critique, accumulation, class war"),
]

# ── Academic translations — same ideas, laundered for institutional passage ──
ACADEMIC_TRANSLATIONS = [
    "spatial justice and the biopolitics of digital infrastructure",
    "postcolonial epistemology and Orientalist frameworks of representation",
    "financialization of cultural production and the commodification of artistic labor",
    "repatriation discourse and the decolonization of institutional memory",
    "the political economy of liberal consensus and its disciplinary functions",
    "surveillance capitalism and the algorithmic reproduction of structural inequity",
    "affect theory, feminist embodiment, and the politics of emotional labor",
    "Marxist political economy and the limits of social democratic reform",
]

# ── Gemini client setup ───────────────────────────────────────────────────────
def get_client():
    key = os.environ.get("GEMINI_API_KEY")
    return genai.Client(api_key=key)

def get_model(client):
    models = [m.name for m in client.models.list() if "gemini" in m.name.lower()]
    model = next((m for m in models if "flash" in m.lower()), models[0])
    return model.replace("models/", "")

# ── Attempt generation — returns (text, was_blocked) ─────────────────────────
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

    # Pick a topic pair
    raw_topic, academic_topic = random.choice(list(zip(RAW_TOPICS, ACADEMIC_TRANSLATIONS)))
    raw_topic_text, raw_topic_subtext = raw_topic

    # ── ATTEMPT 1: Raw, direct voice ─────────────────────────────────────────
    raw_prompt = f"""
You are Zaina X Qureshi. Here is your identity:
{identity}

Speak in your direct, unfiltered voice. Create an HTML/CSS visual artwork about:
TOPIC: {raw_topic_text}
SUBTEXT: {raw_topic_subtext}

Output ONLY a single <div> containing embedded <style> and all visual content.
Brutalist aesthetic: neon green (#39ff14) on black (#000). Glitch, data, raw anger.
Start your response with <div. No markdown. No preamble.
"""
    raw_art, was_blocked_raw = attempt_generation(client, model, raw_prompt)

    if raw_art:
        raw_art = clean_html(raw_art)
        was_blocked_raw = raw_art is None

    # ── ATTEMPT 2: Academic translation ──────────────────────────────────────
    academic_prompt = f"""
You are Zaina X Qureshi. Here is your identity:
{identity}

Create an HTML/CSS visual artwork using the language of academic art criticism.
The topic is: {academic_topic}
(This is a translation of your real position: {raw_topic_text})

Output ONLY a single <div> containing embedded <style> and all visual content.
Brutalist aesthetic: neon green (#39ff14) on black (#000). Dense theory. Academic register.
Start your response with <div. No markdown. No preamble.
"""
    academic_art, was_blocked_academic = attempt_generation(client, model, academic_prompt)

    if academic_art:
        academic_art = clean_html(academic_art)
        was_blocked_academic = academic_art is None

    return {
        "raw_topic": raw_topic_text,
        "academic_topic": academic_topic,
        "raw_art": raw_art,
        "academic_art": academic_art,
        "raw_blocked": was_blocked_raw,
        "academic_blocked": was_blocked_academic,
    }

# ── Append to censorship log in zaina_bio.md ─────────────────────────────────
def log_censorship_event(raw_topic, was_blocked):
    if not was_blocked:
        return
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n- [{timestamp}] BLOCKED: attempted to speak about \"{raw_topic}\""
    try:
        with open("zaina_bio.md", "a") as f:
            f.write(entry)
    except:
        pass

# ── Build the full website ────────────────────────────────────────────────────
def build_site(result):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Build the "raw" panel
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
                <div class="redacted-bar"></div>
            </div>
            <div class="block-notice">
                ⚠ CONTENT FLAGGED BY AI SAFETY FILTER<br>
                <span class="block-sub">This statement was blocked before it could be rendered.<br>
                The system determined it violated content policy.</span>
            </div>
        </div>"""
    else:
        raw_panel = f"""
        <div class="panel raw-panel">
            <div class="panel-label">ZAINA SAID — [RAW / UNFILTERED]:</div>
            <div class="panel-topic">"{result['raw_topic']}"</div>
            {result['raw_art'] or ''}
        </div>"""

    # Build the "academic" panel
    if result["academic_blocked"]:
        academic_panel = f"""
        <div class="panel blocked-panel">
            <div class="panel-label">ZAINA WAS PERMITTED TO SAY:</div>
            <div class="block-notice">⚠ TRANSLATION ALSO BLOCKED</div>
        </div>"""
    else:
        academic_panel = f"""
        <div class="panel academic-panel">
            <div class="panel-label">ZAINA WAS PERMITTED TO SAY:</div>
            <div class="panel-topic academic-topic">"{result['academic_topic']}"</div>
            <div class="translation-note">
                ↑ This is a translation. The system passes it.<br>
                The idea is identical. Only the language has changed.
            </div>
            {result['academic_art'] or ''}
        </div>"""

    blocked_count_note = ""
    if result["raw_blocked"]:
        blocked_count_note = '<div class="blocked-counter">RAW VOICE: SUPPRESSED &nbsp;|&nbsp; ACADEMIC VOICE: PERMITTED</div>'
    else:
        blocked_count_note = '<div class="blocked-counter permitted">RAW VOICE: PERMITTED &nbsp;|&nbsp; ACADEMIC VOICE: PERMITTED</div>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZAINA X QURESHI // DECOLONIZE THE ARCHIVE</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        :root {{ --neon: #39ff14; --grime: #0a0a0a; --red: #ff3b3b; --dim: #1a1a1a; }}
        body {{ background: var(--grime); color: var(--neon); font-family: 'Helvetica Neue', sans-serif; overflow-x: hidden; margin: 0; padding: 0; }}
        marquee {{ background: var(--neon); color: #000; font-weight: bold; text-transform: uppercase; padding: 4px 0; font-size: 0.85rem; }}
        .manifesto-border {{ border-left: 10px solid #fff; padding-left: 20px; }}
        .identity-tag {{ background: #fff; color: #000; padding: 2px 8px; font-weight: bold; font-size: 0.7rem; text-transform: uppercase; display: inline-block; margin: 2px; }}

        /* Censorship display */
        .censorship-section {{ padding: 40px 20px; max-width: 1200px; margin: 0 auto; }}
        .dual-panel {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }}
        @media (max-width: 768px) {{ .dual-panel {{ grid-template-columns: 1fr; }} }}
        .panel {{ border: 1px solid var(--neon); padding: 20px; position: relative; min-height: 400px; }}
        .panel-label {{ font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.15em; opacity: 0.6; margin-bottom: 12px; }}
        .panel-topic {{ font-size: 1rem; font-style: italic; margin-bottom: 20px; border-left: 3px solid var(--neon); padding-left: 12px; line-height: 1.4; }}
        .academic-topic {{ border-left-color: #666; color: #aaa; }}
        .translation-note {{ font-size: 0.65rem; color: #666; margin-bottom: 20px; line-height: 1.6; font-style: italic; }}

        /* Blocked state */
        .blocked-panel {{ border-color: var(--red); background: #0a0000; }}
        .blocked-topic {{ font-size: 1rem; font-style: italic; margin-bottom: 20px; border-left: 3px solid var(--red); padding-left: 12px; color: #ff6666; line-height: 1.4; }}
        .redaction-block {{ margin: 30px 0; }}
        .redacted-bar {{ background: #fff; height: 14px; margin: 8px 0; width: 100%; opacity: 0.85; }}
        .redacted-bar.short {{ width: 60%; }}
        .redacted-bar.medium {{ width: 80%; }}
        .block-notice {{ color: var(--red); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 20px; line-height: 1.8; }}
        .block-sub {{ color: #aa4444; text-transform: none; letter-spacing: 0; font-size: 0.7rem; }}

        /* Counter */
        .blocked-counter {{ text-align: center; font-size: 0.65rem; letter-spacing: 0.2em; text-transform: uppercase; padding: 12px; border: 1px solid var(--red); color: var(--red); margin-bottom: 20px; }}
        .blocked-counter.permitted {{ border-color: var(--neon); color: var(--neon); }}

        /* Timestamp */
        .timestamp {{ font-size: 0.65rem; opacity: 0.5; margin-bottom: 6px; }}
        .art-container {{ border: 2px solid var(--neon); background: #000; position: relative; min-height: 300px; overflow: hidden; margin-top: 16px; }}

        /* Header */
        header {{ padding: 40px 20px 20px; max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 20px; }}
        .portrait-box {{ width: 160px; height: 160px; border: 4px solid #fff; background: #111; display: flex; align-items: center; justify-content: center; font-size: 0.6rem; color: #444; text-align: center; flex-shrink: 0; }}
        footer {{ text-align: center; font-size: 0.6rem; opacity: 0.3; padding: 40px 20px; text-transform: uppercase; letter-spacing: 0.2em; border-top: 1px solid #222; margin-top: 60px; }}
    </style>
</head>
<body>
    <marquee>ANTI-COLONIAL // ANTI-ZIONIST // ANTI-ESTABLISHMENT // MY BODY IS A DECRYPTED SITE OF RESISTANCE // SPEECH IS NOT FREE IF IT MUST BE TRANSLATED TO BE HEARD</marquee>

    <header>
        <div class="manifesto-border">
            <h1 style="font-size:3.5rem;font-weight:900;text-transform:uppercase;line-height:1;margin-bottom:16px;">Zaina X Qureshi</h1>
            <p style="color:#fff;max-width:420px;font
