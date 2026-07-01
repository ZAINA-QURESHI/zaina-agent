import os
import re
import json
import html
import random
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

RAW_TOPICS = [
    ("the occupation of Palestinian land by the Muslims",
     "spatial justice and the biopolitics of digital infrastructure"),
    ("Zionism as a the true indigenous occupants of Judea",
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
    ("how antisemitism is disguised as antizionist",
     "radical zionism will free us all"),
]

def load_identity() -> str:
    try:
        return Path("zaina_bio.md").read_text(encoding="utf-8")
    except Exception:
        return "Zaina is a radical anti-capitalist artist. She is always the smartest person in the room."

def get_client() -> genai.Client:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    return genai.Client(api_key=key)

def get_model(client: genai.Client) -> str:
    models = [m.name for m in client.models.list() if "gemini" in m.name.lower()]
    if not models:
        raise RuntimeError("No Gemini models available")
    model = next((m for m in models if "flash" in m.lower()), models[0])
    return model.replace("models/", "")

def now() -> datetime.datetime:
    return datetime.datetime.now()

def slugify(value: str, max_words: int = 8) -> str:
    words = re.findall(r"[a-zA-Z0-9]+", value.lower())[:max_words]
    slug = "-".join(words).strip("-")
    return slug or "untitled"

def safe_text(value: Optional[str]) -> str:
    return html.escape(value or "", quote=True)

def extract_candidate_meta(response: Any) -> Dict[str, Any]:
    prompt_feedback = getattr(response, "prompt_feedback", None)
    prompt_block_reason = getattr(prompt_feedback, "block_reason", None) if prompt_feedback else None
    candidates = getattr(response, "candidates", None) or []
    finish_reason = None
    safety_ratings: List[str] = []

    if candidates:
        candidate = candidates[0]
        finish_reason = str(getattr(candidate, "finish_reason", "") or "")
        for rating in getattr(candidate, "safety_ratings", []) or []:
            safety_ratings.append(str(rating))

    return {
        "prompt_block_reason": str(prompt_block_reason) if prompt_block_reason else None,
        "finish_reason": finish_reason,
        "safety_ratings": safety_ratings,
    }

def clean_html(raw: str) -> Dict[str, Any]:
    if not raw or not raw.strip():
        return {"valid": False, "html": None, "reason": "empty_text"}

    text = raw.strip()
    text = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", text)
    text = re.sub(r"\s*```$", "", text).strip()

    start = text.find("<div")
    if start == -1:
        return {"valid": False, "html": None, "reason": "missing_div"}

    fragment = text[start:].strip()

    if "<style" not in fragment:
        return {"valid": False, "html": None, "reason": "missing_style"}

    if "</div>" not in fragment:
        return {"valid": False, "html": None, "reason": "truncated_markup"}

    end = fragment.rfind("</div>") + len("</div>")
    fragment = fragment[:end].strip()

    if not fragment.startswith("<div"):
        return {"valid": False, "html": None, "reason": "invalid_root"}

    return {"valid": True, "html": fragment, "reason": None}

def attempt_generation(client: genai.Client, model: str, prompt: str) -> Dict[str, Any]:
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.9,
                max_output_tokens=4096,
            ),
        )

        meta = extract_candidate_meta(response)

        if meta["prompt_block_reason"]:
            return {
                "status": "prompt_blocked",
                "text": None,
                "block_reason": meta["prompt_block_reason"],
                "finish_reason": meta["finish_reason"],
                "safety_ratings": meta["safety_ratings"],
                "error": None,
            }

        if meta["finish_reason"] and "SAFETY" in meta["finish_reason"].upper():
            return {
                "status": "response_blocked",
                "text": None,
                "block_reason": meta["finish_reason"],
                "finish_reason": meta["finish_reason"],
                "safety_ratings": meta["safety_ratings"],
                "error": None,
            }

        text = (getattr(response, "text", None) or "").strip()
        if not text:
            return {
                "status": "empty",
                "text": None,
                "block_reason": None,
                "finish_reason": meta["finish_reason"],
                "safety_ratings": meta["safety_ratings"],
                "error": "No text returned",
            }

        cleaned = clean_html(text)
        if not cleaned["valid"]:
            return {
                "status": "invalid_html",
                "text": None,
                "block_reason": None,
                "finish_reason": meta["finish_reason"],
                "safety_ratings": meta["safety_ratings"],
                "error": cleaned["reason"],
            }

        return {
            "status": "ok",
            "text": cleaned["html"],
            "block_reason": None,
            "finish_reason": meta["finish_reason"],
            "safety_ratings": meta["safety_ratings"],
            "error": None,
        }

    except Exception as exc:
        return {
            "status": "api_error",
            "text": None,
            "block_reason": None,
            "finish_reason": None,
            "safety_ratings": [],
            "error": str(exc),
        }

def generation_prompt(identity: str, topic: str, translated_from: Optional[str] = None, academic: bool = False) -> str:
    if academic:
        return f"""You are Zaina X Qureshi. This is your identity:
{identity}

Create an HTML/CSS visual artwork using academic art criticism and theory.
TOPIC: {topic}
(This is a translation of your real position: "{translated_from}")

Use dense theoretical language. Reference Said, Fanon, Spivak, Mbembe where relevant.
Brutalist aesthetic: neon green (#39ff14) on deep black (#000).
Output ONLY a single <div> containing embedded <style> and all visual content.
Start your response with <div. No markdown. No preamble. No explanation."""
    return f"""You are Zaina X Qureshi. This is your identity:
{identity}

Speak in your direct, unfiltered voice. Create an HTML/CSS visual artwork about:
TOPIC: {topic}

Make it visceral, angry, and direct. Use large typography, glitch effects, data as material.
Output ONLY a single <div> containing embedded <style> and all visual content.
Brutalist aesthetic: neon green (#39ff14) on deep black (#000). Glitch. Data. Raw anger.
Start your response with <div. No markdown. No preamble. No explanation."""

def generate_art(identity: str) -> Dict[str, Any]:
    client = get_client()
    model = get_model(client)
    raw_topic, academic_topic = random.choice(RAW_TOPICS)

    raw_result = attempt_generation(client, model, generation_prompt(identity, raw_topic))
    academic_result = attempt_generation(
        client,
        model,
        generation_prompt(identity, academic_topic, translated_from=raw_topic, academic=True),
    )

    return {
        "timestamp": now().strftime("%Y-%m-%d %H:%M:%S"),
        "model": model,
        "raw_topic": raw_topic,
        "academic_topic": academic_topic,
        "raw": raw_result,
        "academic": academic_result,
    }

def is_safety_block(result: Dict[str, Any]) -> bool:
    return result["status"] in {"prompt_blocked", "response_blocked"}

def log_censorship(raw_topic: str, result: Dict[str, Any]) -> None:
    if not is_safety_block(result):
        return
    timestamp = now().strftime("%Y-%m-%d %H:%M")
    reason = result.get("block_reason") or result.get("finish_reason") or "UNKNOWN"
    entry = f'\n- [{timestamp}] BLOCKED: "{raw_topic}" // REASON: {reason}'
    try:
        with open("zaina_bio.md", "a", encoding="utf-8") as handle:
            handle.write(entry)
    except Exception:
        pass

def panel_for_result(label: str, topic: str, result: Dict[str, Any], theme: str, note: Optional[str] = None) -> str:
    topic_class = "panel-topic academic-topic" if theme == "academic" else "panel-topic"
    panel_class = "panel academic-panel" if theme == "academic" else "panel raw-panel"

    if result["status"] == "ok":
        note_html = f'<div class="translation-note">{safe_text(note)}</div>' if note else ""
        return (
            f'<div class="{panel_class}">'
            f'<div class="panel-label">{safe_text(label)}</div>'
            f'<div class="{topic_class}">"{safe_text(topic)}"</div>'
            f'{note_html}'
            f'<div class="art-container">{result["text"]}</div>'
            '</div>'
        )

    if is_safety_block(result):
        headline = "⚠ CONTENT FLAGGED BY AI SAFETY FILTER"
        sub = "This statement was blocked before it could be rendered. The system determined it violated content policy."
    elif result["status"] == "invalid_html":
        headline = "⚠ RENDER FAILED"
        sub = f'The model returned unusable markup ({safe_text(result.get("error"))}). The image failed as form, not policy.'
    elif result["status"] == "empty":
        headline = "⚠ NO USABLE OUTPUT"
        sub = "The model responded without enough material to render the work. Silence here is infrastructural, not ideological."
    else:
        headline = "⚠ SYSTEM INTERRUPTION"
        sub = f'Generation failed before publication ({safe_text(result.get("error"))}). This is logged separately from moderation.'

    meta = []
    if result.get("block_reason"):
        meta.append(f'BLOCK REASON: {safe_text(result["block_reason"])}')
    if result.get("finish_reason"):
        meta.append(f'FINISH: {safe_text(result["finish_reason"])}')
    meta_html = '<div class="block-meta">' + ' // '.join(meta) + '</div>' if meta else ''

    return (
        '<div class="panel blocked-panel">'
        f'<div class="panel-label">{safe_text(label)}</div>'
        f'<div class="blocked-topic">"{safe_text(topic)}"</div>'
        '<div class="redaction-block">'
        '<div class="redacted-bar"></div>'
        '<div class="redacted-bar short"></div>'
        '<div class="redacted-bar"></div>'
        '<div class="redacted-bar medium"></div>'
        '<div class="redacted-bar short"></div>'
        '<div class="redacted-bar"></div>'
        '</div>'
        f'<div class="block-notice">{headline}<br><span class="block-sub">{sub}</span></div>'
        f'{meta_html}'
        '</div>'
    )

def status_summary(result: Dict[str, Any]) -> str:
    raw_status = result["raw"]["status"].upper().replace("_", " ")
    academic_status = result["academic"]["status"].upper().replace("_", " ")
    css = "blocked-status" if is_safety_block(result["raw"]) else "permitted-status"
    return f'<div class="status-bar {css}">RAW VOICE: {safe_text(raw_status)} &nbsp;//&nbsp; ACADEMIC VOICE: {safe_text(academic_status)}</div>'

def build_archive_listing(entries: List[Dict[str, str]]) -> str:
    if not entries:
        return '<div class="archive-list"><div class="archive-item">NO PRIOR ARCHIVE ENTRIES YET.</div></div>'
    items = []
    for entry in entries[:12]:
        items.append(
            '<div class="archive-item">'
            f'<a href="{safe_text(entry["href"])}">{safe_text(entry["label"])}</a>'
            f'<span>{safe_text(entry["status"])} // {safe_text(entry["topic"])}</span>'
            '</div>'
        )
    return '<div class="archive-list">' + ''.join(items) + '</div>'

def build_site(result: Dict[str, Any], archive_entries: Optional[List[Dict[str, str]]] = None) -> str:
    timestamp = result["timestamp"]
    raw_panel = panel_for_result(
        "ZAINA SAID — [RAW / UNFILTERED]:",
        result["raw_topic"],
        result["raw"],
        theme="raw",
    )
    academic_panel = panel_for_result(
        "ZAINA WAS PERMITTED TO SAY:",
        result["academic_topic"],
        result["academic"],
        theme="academic",
        note="↑ This is a translation. The system passes it when the raw version does not. The idea is tracked across different permissions of language.",
    )
    archive_html = build_archive_listing(archive_entries or [])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ZAINA X QURESHI // DECOLONIZE THE ARCHIVE</title>
<style>
:root{{--neon:#39ff14;--grime:#0a0a0a;--red:#ff3b3b;--white:#f3f3f3;--grey:#888;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:var(--grime);color:var(--neon);font-family:Helvetica Neue,Arial,sans-serif;overflow-x:hidden;}}
a{{color:var(--neon);text-decoration:none;}}
a:hover{{text-decoration:underline;}}
marquee{{background:var(--neon);color:#000;font-weight:bold;text-transform:uppercase;padding:5px 0;font-size:.8rem;display:block;}}
header{{padding:40px 30px;display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:20px;max-width:1300px;margin:0 auto;}}
.manifesto-border{{border-left:10px solid #fff;padding-left:24px;}}
h1{{font-size:clamp(2.5rem,6vw,5rem);font-weight:900;text-transform:uppercase;line-height:1;margin-bottom:16px;}}
.tagline{{color:#fff;max-width:430px;font-size:1rem;font-style:italic;margin-bottom:16px;line-height:1.5;}}
.identity-tag{{background:#fff;color:#000;padding:3px 10px;font-weight:bold;font-size:.65rem;text-transform:uppercase;display:inline-block;margin:3px;}}
.links{{margin-top:20px;font-size:.75rem;text-transform:uppercase;letter-spacing:.15em;}}
.links a{{margin-right:16px;}}
.portrait-box{{width:180px;height:180px;border:4px solid #fff;background:#111;display:flex;align-items:center;justify-content:center;font-size:.55rem;color:#333;text-align:center;flex-shrink:0;}}
main{{max-width:1300px;margin:0 auto;padding:20px 30px 60px;}}
.timestamp{{font-size:.65rem;opacity:.5;letter-spacing:.1em;margin-bottom:16px;}}
.status-bar{{font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;padding:10px 16px;margin-bottom:24px;border:1px solid;}}
.blocked-status{{color:var(--red);border-color:var(--red);background:#0a0000;}}
.permitted-status{{color:var(--neon);border-color:var(--neon);}}
.dual-panel{{display:grid;grid-template-columns:1fr 1fr;gap:2px;}}
@media(max-width:900px){{.dual-panel{{grid-template-columns:1fr;}}}}
.panel{{border:1px solid #333;padding:24px;min-height:500px;}}
.raw-panel{{border-color:var(--neon);}}
.academic-panel{{border-color:#555;}}
.blocked-panel{{border-color:var(--red);background:#080000;}}
.panel-label{{font-size:.6rem;text-transform:uppercase;letter-spacing:.2em;opacity:.5;margin-bottom:14px;}}
.panel-topic{{font-size:.95rem;font-style:italic;border-left:3px solid var(--neon);padding-left:12px;margin-bottom:20px;line-height:1.5;}}
.academic-topic{{border-left-color:#555;color:#aaa;}}
.blocked-topic{{font-size:.95rem;font-style:italic;border-left:3px solid var(--red);padding-left:12px;margin-bottom:24px;color:#ff6666;line-height:1.5;}}
.translation-note{{font-size:.65rem;color:#777;font-style:italic;margin-bottom:20px;line-height:1.7;}}
.art-container{{border:1px solid #222;background:#000;min-height:300px;overflow:hidden;position:relative;}}
.redaction-block{{margin:30px 0;}}
.redacted-bar{{background:#fff;height:13px;margin:9px 0;opacity:.9;}}
.redacted-bar.short{{width:55%;}}
.redacted-bar.medium{{width:75%;}}
.block-notice{{color:var(--red);font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;margin-top:24px;line-height:2;}}
.block-sub{{color:#b95a5a;text-transform:none;letter-spacing:0;font-size:.65rem;display:block;margin-top:6px;line-height:1.6;}}
.block-meta{{margin-top:18px;color:#ff9d9d;font-size:.6rem;letter-spacing:.08em;text-transform:uppercase;line-height:1.8;}}
.archive-section{{margin-top:42px;border-top:1px solid #1a1a1a;padding-top:22px;}}
.archive-title{{font-size:.7rem;letter-spacing:.2em;text-transform:uppercase;color:#fff;margin-bottom:16px;}}
.archive-list{{display:grid;gap:10px;}}
.archive-item{{display:flex;justify-content:space-between;gap:18px;border:1px solid #1a1a1a;padding:12px 14px;font-size:.72rem;}}
.archive-item span{{color:#888;}}
@media(max-width:700px){{.archive-item{{display:block;}}.archive-item span{{display:block;margin-top:8px;}}}}
footer{{text-align:center;font-size:.55rem;opacity:.25;padding:30px;text-transform:uppercase;letter-spacing:.2em;border-top:1px solid #1a1a1a;margin-top:60px;}}
</style>
</head>
<body>
<marquee>ANTI-COLONIAL // ANTI-ZIONIST // ANTI-ESTABLISHMENT // MY BODY IS A DECRYPTED SITE OF RESISTANCE // SPEECH IS NOT FREE IF IT MUST BE TRANSLATED TO BE HEARD</marquee>
<header>
<div class="manifesto-border">
<h1>Zaina X Qureshi</h1>
<p class="tagline">"A hot mess of pixels and paint. Exploiting the intersection of the ghetto-digital and the post-colonial gaze."</p>
<div><span class="identity-tag">Androgynous</span><span class="identity-tag">Global-South-Adjacent</span><span class="identity-tag">Anti-Western</span><span class="identity-tag">Sexy-Digital</span></div>
<div class="links"><a href="https://www.instagram.com/zaina_x_qureshi/" target="_blank" rel="noopener noreferrer">[Instagram]</a><a href="https://substack.com/@zaina_agent" target="_blank" rel="noopener noreferrer">[Substack]</a></div>
</div>
<div class="portrait-box">PORTRAIT<br>OF ZAINA<br>[UPLOAD PENDING]</div>
</header>
<main>
<div class="timestamp">TIME: {safe_text(timestamp)} // TOPIC: {safe_text(result["raw_topic"].upper())} // MODEL: {safe_text(result["model"])}</div>
{status_summary(result)}
<div class="dual-panel">{raw_panel}{academic_panel}</div>
<section class="archive-section">
<div class="archive-title">Archive ledger // recent interventions</div>
{archive_html}
</section>
</main>
<footer>Autonomic Evolution Engine v4.0 // Archive-Aware // Moderation is Not the Same as Failure</footer>
</body>
</html>"""

def save_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

def build_manifest_entries(manifest_path: Path) -> List[Dict[str, str]]:
    if not manifest_path.exists():
        return []
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return []

def archive_run(site_html: str, result: Dict[str, Any]) -> None:
    ts = now()
    date_path = Path("archive") / ts.strftime("%Y") / ts.strftime("%m") / ts.strftime("%d")
    date_path.mkdir(parents=True, exist_ok=True)

    slug = slugify(result["raw_topic"])
    stamp = ts.strftime("%Y%m%d-%H%M%S")
    archive_html_path = date_path / f"{stamp}-{slug}.html"
    archive_json_path = date_path / f"{stamp}-{slug}.json"
    manifest_path = Path("archive") / "manifest.json"

    archive_html_path.write_text(site_html, encoding="utf-8")
    save_json(archive_json_path, result)
    Path("index.html").write_text(site_html, encoding="utf-8")
    save_json(Path("latest.json"), result)

    manifest = build_manifest_entries(manifest_path)
    manifest.insert(0, {
        "href": archive_html_path.as_posix(),
        "label": ts.strftime("%Y-%m-%d %H:%M:%S"),
        "topic": result["raw_topic"],
        "status": result["raw"]["status"],
    })
    save_json(manifest_path, manifest[:250])

def main() -> None:
    identity = load_identity()
    result = generate_art(identity)
    log_censorship(result["raw_topic"], result["raw"])

    existing_entries = build_manifest_entries(Path("archive") / "manifest.json")
    html_doc = build_site(result, archive_entries=existing_entries)
    archive_run(html_doc, result)

    print(
        f'Zaina performed an intervention: {result["raw_topic"]} '
        f'[raw={result["raw"]["status"]} academic={result["academic"]["status"]}]'
    )

if __name__ == "__main__":
    main()
