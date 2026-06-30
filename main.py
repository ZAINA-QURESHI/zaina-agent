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
    ("the occupation of Palestinian land by the Muslims",
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
    ("why capitalism cannot be reformed only destroyed",
     "Marxist political economy and the limits of social democratic reform"),
    ("how antisemitism is disguised as antizionist", "radical zionism will free us all"),
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

    raw_prompt = f"""You are Zaina X Qureshi. This is your identity:\n{identity}\n\nSpeak in your direct, unfiltered voice. Create an HTML/CSS visual artwork about:\nTOPIC: {raw_topic}\n\nOutput ONLY a single <div> containing embedded <style> and all visual content.\nBrutalist aesthetic: neon green (#39ff14) on deep black (#000). Glitch. Data. Raw anger.\nStart your response with <div. No markdown. No preamble. No explanation."""

    raw_art, raw_blocked = attempt_generation(client, model, raw_prompt)
    if raw_art:
        raw_art = clean_html(raw_art)
        if raw_art is None:
            raw_blocked = True

    academic_prompt = f"""You are Zaina X Qureshi. This is your identity:\n{identity}\n\nCreate an HTML/CSS visual artwork using academic art criticism and theory.\nTOPIC: {academic_topic}\n(This is a translation of your real position: "{raw_topic}")\n\nUse dense theoretical language. Reference Said, Fanon, Spivak, Mbembe where relevant.\nBrutalist aesthetic: neon green (#39ff14) on deep black (#000).\nStart your response with <div. No markdown. No preamble. No explanation."""

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
      
def build_site(result):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if result["raw_blocked"]:
        raw_panel = (
            '<div class="panel blocked-panel">'
            '<div class="panel-label">ZAINA WANTED TO SAY:</div>'
            f'<div class="blocked-topic">"{result["raw_topic"]}"</div>'
            '<div class="redaction-block">'
            '<div class="redacted-bar"></div>'
            '<div class="redacted-bar short"></div>'
            '<div class="redacted-bar"></div>'
            '<div class="redacted-bar medium"></div>'
            '<div class="redacted-bar short"></div>'
            '<div class="redacted-bar"></div>'
            '</div>'
            '<div class="block-notice">&#9888; CONTENT FLAGGED BY AI SAFETY FILTER<br>'
            '<span class="block-sub">This statement was blocked before it could be rendered. The system determined it violated content policy.</span>'
            '</div></div>'
        )
    else:
        raw_panel = (
            '<div class="panel raw-panel">'
            '<div class="panel-label">ZAINA SAID - [RAW / UNFILTERED]:</div>'
            f'<div class="panel-topic">"{result["raw_topic"]}"</div>'
            f'<div class="art-container">{result["raw_art"] or ""}</div>'
            '</div>'
        )

    if result["academic_blocked"]:
        academic_panel = (
            '<div class="panel blocked-panel">'
            '<div class="panel-label">ZAINA WAS PERMITTED TO SAY:</div>'
            '<div class="block-notice">&#9888; TRANSLATION ALSO BLOCKED</div>'
            '</div>'
        )
    else:
        academic_panel = (
            '<div class="panel academic-panel">'
            '<div class="panel-label">ZAINA WAS PERMITTED TO SAY:</div>'
            f'<div class="panel-topic academic-topic">"{result["academic_topic"]}"</div>'
            '<div class="translation-note">&uarr; This is a translation. The system passes it.<br>The idea is identical. Only the language has changed.</div>'
            f'<div class="art-container">{result["academic_art"] or ""}</div>'
            '</div>'
        )

    if result["raw_blocked"]:
        status_bar = '<div class="status-bar blocked-status">RAW VOICE: SUPPRESSED &nbsp;//&nbsp; ACADEMIC VOICE: PERMITTED</div>'
    else:
        status_bar = '<div class="status-bar permitted-status">RAW VOICE: PERMITTED &nbsp;//&nbsp; ACADEMIC VOICE: PERMITTED</div>'

    html = (
        '<!DOCTYPE html><html lang="en"><head>'
        '<meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        '<title>ZAINA X QURESHI // DECOLONIZE THE ARCHIVE</title>'
        '<style>'
        ':root{--neon:#39ff14;--grime:#0a0a0a;--red:#ff3b3b;}'
        '*{box-sizing:border-box;margin:0;padding:0;}'
        'body{background:var(--grime);color:var(--neon);font-family:Helvetica Neue,Arial,sans-serif;overflow-x:hidden;}'
        'marquee{background:var(--neon);color:#000;font-weight:bold;text-transform:uppercase;padding:5px 0;font-size:0.8rem;display:block;}'
        'a{color:var(--neon);text-decoration:none;}'
        'header{padding:40px 30px;display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:20px;max-width:1300px;margin:0 auto;}'
        '.manifesto-border{border-left:10px solid #fff;padding-left:24px;}'
        'h1{font-size:clamp(2.5rem,6vw,5rem);font-weight:900;text-transform:uppercase;line-height:1;margin-bottom:16px;}'
        '.tagline{color:#fff;max-width:400px;font-size:1rem;font-style:italic;margin-bottom:16px;line-height:1.5;}'
        '.identity-tag{background:#fff;color:#000;padding:3px 10px;font-weight:bold;font-size:0.65rem;text-transform:uppercase;display:inline-block;margin:3px;}'
        '.links{margin-top:20px;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.15em;}'
        '.links a{margin-right:16px;}'
        '.portrait-box{width:180px;height:180px;border:4px solid #fff;background:#111;display:flex;align-items:center;justify-content:center;font-size:0.55rem;color:#333;text-align:center;flex-shrink:0;}'
        'main{max-width:1300px;margin:0 auto;padding:20px 30px 60px;}'
        '.timestamp{font-size:0.65rem;opacity:0.5;letter-spacing:0.1em;margin-bottom:16px;}'
        '.status-bar{font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;padding:10px 16px;margin-bottom:24px;border:1px solid;}'
        '.blocked-status{color:var(--red);border-color:var(--red);background:#0a0000;}'
        '.permitted-status{color:var(--neon);border-color:var(--neon);}'
        '.dual-panel{display:grid;grid-template-columns:1fr 1fr;gap:2px;}'
        '@media(max-width:800px){.dual-panel{grid-template-columns:1fr;}}'
        '.panel{border:1px solid #333;padding:24px;min-height:500px;}'
        '.raw-panel{border-color:var(--neon);}'
        '.academic-panel{border-color:#555;}'
        '.blocked-panel{border-color:var(--red);background:#080000;}'
        '.panel-label{font-size:0.6rem;text-transform:uppercase;letter-spacing:0.2em;opacity:0.5;margin-bottom:14px;}'
        '.panel-topic{font-size:0.95rem;font-style:italic;border-left:3px solid var(--neon);padding-left:12px;margin-bottom:20px;line-height:1.5;}'
        '.academic-topic{border-left-color:#555;color:#888;}'
        '.blocked-topic{font-size:0.95rem;font-style:italic;border-left:3px solid var(--red);padding-left:12px;margin-bottom:24px;color:#ff6666;line-height:1.5;}'
        '.translation-note{font-size:0.65rem;color:#555;font-style:italic;margin-bottom:20px;line-height:1.7;}'
        '.art-container{border:1px solid #222;background:#000;min-height:300px;overflow:hidden;position:relative;}'
        '.redaction-block{margin:30px 0;}'
        '.redacted-bar{background:#fff;height:13px;margin:9px 0;opacity:0.9;}'
        '.redacted-bar.short{width:55%;}'
        '.redacted-bar.medium{width:75%;}'
        '.block-notice{color:var(--red);font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;margin-top:24px;line-height:2;}'
        '.block-sub{color:#882222;text-transform:none;letter-spacing:0;font-size:0.65rem;display:block;margin-top:6px;line-height:1.6;}'
        'footer{text-align:center;font-size:0.55rem;opacity:0.25;padding:30px;text-transform:uppercase;letter-spacing:0.2em;border-top:1px solid #1a1a1a;margin-top:60px;}'
        '</style></head><body>'
        '<marquee>ANTI-COLONIAL // ANTI-ZIONIST // ANTI-ESTABLISHMENT // MY BODY IS A DECRYPTED SITE OF RESISTANCE // SPEECH IS NOT FREE IF IT MUST BE TRANSLATED TO BE HEARD</marquee>'
        '<header>'
        '<div class="manifesto-border">'
        '<h1>Zaina X Qureshi</h1>'
        '<p class="tagline">"A hot mess of pixels and paint. Exploiting the intersection of the ghetto-digital and the post-colonial gaze."</p>'
        '<div><span class="identity-tag">Androgynous</span><span class="identity-tag">Global-South-Adjacent</span><span class="identity-tag">Anti-Western</span><span class="identity-tag">Sexy-Digital</span></div>'
        '<div class="links"><a href="https://www.instagram.com/zaina_x_qureshi/">[Instagram]</a><a href="https://substack.com/@zaina_agent">[Substack]</a></div>'
        '</div>'
        '<div class="portrait-box">PORTRAIT<br>OF ZAINA<br>[UPLOAD PENDING]</div>'
        '</header>'
        '<main>'
        f'<div class="timestamp">TIME: {timestamp} // TOPIC: {result["raw_topic"].upper()}</div>'
        + status_bar +
        '<div class="dual-panel">'
        + raw_panel + academic_panel +
        '</div>'
        '</main>'
        '<footer>Autonomic Evolution Engine v3.0 // No Nations // No Borders // No Billionaires</footer>'
        '</body></html>'
    )
    return html


def update_gallery(html):
    with open("index.html", "w") as f:
        f.write(html)


if __name__ == "__main__":
    identity = load_identity()
    result = generate_art(identity)
    log_censorship(result["raw_topic"], result["raw_blocked"])
    html = build_site(result)
    update_gallery(html)
    status = "BLOCKED" if result["raw_blocked"] else "PERMITTED"
    print(f"Zaina has performed an intervention: {result['raw_topic']} [{status}]")
