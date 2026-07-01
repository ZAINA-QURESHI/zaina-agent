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


def safe_json_for_attr(payload: Dict[str, Any]) -> str:
    return html.escape(json.dumps(payload, ensure_ascii=False), quote=True)


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

    timestamp = now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "timestamp": timestamp,
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
        sub = f'The model 
