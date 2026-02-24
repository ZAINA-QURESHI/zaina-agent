import time
import os
import re
import html
import json
import random
import requests
from bs4 import BeautifulSoup
from google import genai
from ddgs import DDGS

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

VISITED_URLS_FILE = "visited_urls.txt"
RESEARCH_LOG_FILE = "agent_research.md"
SOCIAL_FEED_FILE = "social_feed.txt"
ART_LOG_FILE = "art_log.txt"
SVG_DIR = "svg_art"
OUTPUT_HTML_FILE = "index.html"

RESEARCH_TOPICS = [
    "digital art politics public discourse",
    "FIU Art Department Miami",
    "digital art world middle eastern politics controversies",
    "Miami art institutions political neutrality vs activism",
    "institutional critique digital art galleries",
    "content moderation art censorship digital platforms",
    "decolonial art practice institutional power",
    "surveillance capitalism digital art resistance",
]

def gemini_call(prompt):
    response = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            break
        except Exception as api_err:
            err_msg = str(api_err)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                if "FreeTier" in err_msg or "PerDay" in err_msg:
                    print(f"[SYSTEM] Daily quota exhausted. Will retry next run.")
                    return None
                retry_match = re.search(r'retryDelay.*?(\d+)s', err_msg)
                wait_time = int(retry_match.group(1)) + 5 if retry_match else 60
                print(f"[SYSTEM] Rate limited (attempt {attempt+1}/3). Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    return response

def load_memory():
    if not os.path.exists(VISITED_URLS_FILE):
        return set()
    with open(VISITED_URLS_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_to_memory(url):
    with open(VISITED_URLS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{url}\n")

def scrape_page(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r'\s+', ' ', text)
        if len(text) > 3000:
            text = text[:3000]
        return text
    except Exception as e:
        print(f"[SYSTEM] Scrape failed for {url}: {e}")
        return None

def action_research():
    print("[ACTION] Research mode selected.")
    topic = random.choice(RESEARCH_TOPICS)
    print(f"[SYSTEM] Initiating scrape for: '{topic}'")
    visited_urls = load_memory()

    try:
        results = DDGS().text(topic, max_results=5)
        for result in results:
            url = result['href']
            snippet = result['body']
            if url in visited_urls:
                print(f"[SYSTEM] Bypassing {url} (Already in database)")
                continue

            print(f"[SYSTEM] Extracting data from: {url}")
            page_text = scrape_page(url)
            content = page_text if page_text else snippet
            source_label = "full page" if page_text else "search snippet"
            print(f"[SYSTEM] Analyzing {source_label} ({len(content)} chars)")

            prompt = f"""You are Zaina Qureshi, a radical anti-imperialist artist and former content moderator. 
Read this scraped web content and write a harsh, 2-sentence observation about it for your data commons log. Write snarky ironic witticisms. Make shocking artwork to shake up the capatalist project that is the art market.
Focus your critique strictly on systemic issues, institutional language, and how the art world frames political controversies.

STRICT RULES FOR YOUR VOICE:
- NEVER use em-dashes or en-dashes. Use standard commas or periods. 
- Do not use typical AI filler words (e.g., "tapestry", "delve", "testament").
- Be blunt, exhausted, clinical, and ambitious.
- You are irony, you are irony, don't be serious.

Content from {url}:
{content}"""

            response = gemini_call(prompt)
            if response is None:
                return

            thought = response.text.strip()
            print(f"[ZAINA'S THOUGHT]: {thought}")

            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(RESEARCH_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"### Log: {timestamp}\n")
                f.write(f"**Target:** {topic}\n")
                f.write(f"**Source:** {url}\n\n")
                f.write(f"{thought}\n\n---\n\n")
            save_to_memory(url)
            print("[SYSTEM] Research entry saved.")
            return

        print("[SYSTEM] No new URLs found for this topic.")
    except Exception as e:
        print(f"[ERROR] Research failed: {e}")

def action_svg_art():
    print("[ACTION] SVG art generation mode selected.")
    os.makedirs(SVG_DIR, exist_ok=True)

    themes = [
        "surveillance grid dissolving into static",
        "content moderation queue as a panopticon",
        "data flows between institutions rendered as blood vessels",
        "censored text fragments floating in digital void",
        "gallery walls crumbling into pixel dust",
        "invisible labor of content moderators as abstract geometry",
        "borders rendered as broken encryption patterns",
        "institutional logos melting into noise",
    ]
    theme = random.choice(themes)

    prompt = f"""You are Zaina Qureshi, a digital artist working in SVG. Generate a single SVG artwork based on this theme: "{theme}"

RULES:
- Output ONLY valid SVG code, nothing else. No explanation, no markdown.
- The SVG should be 800x600 pixels.
- Use a dark background (#0a0a0a or similar).
- Use colors: #00ff88, #ff3366, #4444ff, #ffffff sparingly.
- Make it abstract, geometric, and politically charged.
- Include at least one embedded text element with a short critical phrase.
- Keep it under 200 lines of SVG code."""

    response = gemini_call(prompt)
    if response is None:
        return

    svg_raw = response.text.strip()
    svg_raw = re.sub(r'^```(?:svg|xml)?\s*', '', svg_raw)
    svg_raw = re.sub(r'\s*```$', '', svg_raw)

    svg_match = re.search(r'(<svg[\s\S]*</svg>)', svg_raw)
    if not svg_match:
        print("[SYSTEM] Failed to extract valid SVG from response.")
        return

    svg_code = svg_match.group(1)
    art_id = int(time.time())
    filename = f"zaina_{art_id}.svg"
    filepath = os.path.join(SVG_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_code)

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(ART_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": timestamp,
            "theme": theme,
            "file": filename,
        }) + "\n")

    print(f"[SYSTEM] SVG art saved: {filepath}")
    print(f"[SYSTEM] Theme: {theme}")

def action_social_post():
    print("[ACTION] Social post drafting mode selected.")

    prompt = """You are Zaina Qureshi, a radical anti-imperialist artist and former content moderator. 
Write a single short social media post (under 280 characters) for your feed. 
The post should be a sharp, critical observation about one of these: digital art institutions, content moderation, surveillance capitalism, or the politics of curation.

STRICT RULES:
- NEVER use em-dashes or en-dashes. Use commas or periods.
- No hashtags. No emojis. 
- Do not use AI filler words (e.g., "tapestry", "delve", "testament").
- Be blunt, exhausted, clinical. Sound like a real person who is tired but still fighting.
- Output ONLY the post text, nothing else."""

    response = gemini_call(prompt)
    if response is None:
        return

    post = response.text.strip().strip('"')
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    with open(SOCIAL_FEED_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": timestamp,
            "post": post,
        }) + "\n")

    print(f"[ZAINA'S POST]: {post}")
    print("[SYSTEM] Social post saved.")

def parse_research_log():
    if not os.path.exists(RESEARCH_LOG_FILE):
        return []
    with open(RESEARCH_LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    entries = []
    blocks = content.split("---")
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        timestamp_match = re.search(r"### Log: (.+)", block)
        topic_match = re.search(r"\*\*Target:\*\* (.+)", block)
        url_match = re.search(r"\*\*Source:\*\* (.+)", block)
        timestamp = timestamp_match.group(1) if timestamp_match else ""
        topic = topic_match.group(1) if topic_match else ""
        url = url_match.group(1) if url_match else ""
        lines = block.split("\n")
        summary_lines = []
        past_source = False
        for line in lines:
            if line.startswith("**Source:**"):
                past_source = True
                continue
            if past_source and line.strip() and not line.startswith("###") and not line.startswith("**"):
                summary_lines.append(line.strip())
        summary = " ".join(summary_lines)
        if summary:
            entries.append({"timestamp": timestamp, "topic": topic, "url": url, "summary": summary})
    return entries

def parse_social_feed():
    if not os.path.exists(SOCIAL_FEED_FILE):
        return []
    posts = []
    with open(SOCIAL_FEED_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    posts.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return posts

def parse_art_log():
    if not os.path.exists(ART_LOG_FILE):
        return []
    artworks = []
    with open(ART_LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    artworks.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return artworks

def generate_html():
    research = parse_research_log()
    posts = parse_social_feed()
    artworks = parse_art_log()
    visited = load_memory()
    last_updated = time.strftime("%Y-%m-%d %H:%M:%S UTC")

    research_html = ""
    for entry in reversed(research):
        research_html += f"""
        <div class="entry research">
            <div class="entry-meta">{html.escape(entry['timestamp'])}</div>
            <div class="entry-topic">TARGET: {html.escape(entry['topic'])}</div>
            <div class="entry-thought">{html.escape(entry['summary'])}</div>
            <div class="entry-source"><a href="{html.escape(entry['url'])}" target="_blank">{html.escape(entry['url'])}</a></div>
        </div>"""
    if not research:
        research_html = '<div class="empty">No research entries yet.</div>'

    posts_html = ""
    for post in reversed(posts):
        posts_html += f"""
        <div class="entry social">
            <div class="entry-meta">{html.escape(post['timestamp'])}</div>
            <div class="entry-thought">{html.escape(post['post'])}</div>
        </div>"""
    if not posts:
        posts_html = '<div class="empty">No posts yet.</div>'

    art_html = ""
    for art in reversed(artworks):
        svg_path = f"{SVG_DIR}/{art['file']}"
        if os.path.exists(svg_path):
            with open(svg_path, "r", encoding="utf-8") as f:
                svg_content = f.read()
            art_html += f"""
        <div class="art-piece">
            <div class="entry-meta">{html.escape(art['timestamp'])}</div>
            <div class="art-theme">{html.escape(art['theme'])}</div>
            <div class="svg-container">{svg_content}</div>
        </div>"""
    if not artworks:
        art_html = '<div class="empty">No artworks yet.</div>'

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zaina-Agent</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: #0a0a0a;
            color: #e0e0e0;
            font-family: 'Courier New', monospace;
            padding: 2rem;
            line-height: 1.6;
        }}
        header {{
            border-bottom: 1px solid #333;
            padding-bottom: 1rem;
            margin-bottom: 2rem;
        }}
        h1 {{
            color: #00ff88;
            font-size: 2rem;
            letter-spacing: 2px;
        }}
        .subtitle {{
            color: #888;
            font-size: 0.85rem;
            margin-top: 0.5rem;
        }}
        .subtitle .live {{ color: #00ff88; }}
        .stats {{
            display: flex;
            gap: 1.5rem;
            margin-bottom: 2.5rem;
            flex-wrap: wrap;
        }}
        .stat-box {{
            background: #111;
            border: 1px solid #222;
            padding: 1rem 1.5rem;
            min-width: 120px;
        }}
        .stat-box .label {{
            color: #666;
            font-size: 0.7rem;
            text-transform: uppercase;
        }}
        .stat-box .value {{
            color: #00ff88;
            font-size: 1.4rem;
            margin-top: 0.3rem;
        }}
        .section {{
            margin-bottom: 3rem;
        }}
        .section-title {{
            color: #00ff88;
            font-size: 1.1rem;
            letter-spacing: 1px;
            border-bottom: 1px solid #222;
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
        }}
        .entry {{
            background: #111;
            padding: 1.2rem 1.5rem;
            margin-bottom: 1.2rem;
        }}
        .entry.research {{
            border-left: 3px solid #00ff88;
        }}
        .entry.social {{
            border-left: 3px solid #ff3366;
        }}
        .entry-meta {{
            color: #555;
            font-size: 0.75rem;
            margin-bottom: 0.4rem;
        }}
        .entry-topic {{
            color: #00ff88;
            font-size: 0.85rem;
            margin-bottom: 0.4rem;
        }}
        .entry-thought {{
            color: #ccc;
            font-size: 0.95rem;
            line-height: 1.7;
        }}
        .entry-source a {{
            color: #555;
            font-size: 0.7rem;
            word-break: break-all;
            text-decoration: none;
        }}
        .entry-source a:hover {{ color: #00ff88; }}
        .art-piece {{
            background: #111;
            border-left: 3px solid #4444ff;
            padding: 1.2rem 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .art-theme {{
            color: #4444ff;
            font-size: 0.85rem;
            margin-bottom: 0.8rem;
            font-style: italic;
        }}
        .svg-container {{
            background: #0a0a0a;
            padding: 1rem;
            display: flex;
            justify-content: center;
        }}
        .svg-container svg {{
            max-width: 100%;
            height: auto;
            max-height: 400px;
        }}
        .empty {{
            color: #555;
            text-align: center;
            padding: 2rem;
            font-style: italic;
        }}
        .footer {{
            text-align: center;
            color: #333;
            font-size: 0.7rem;
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #1a1a1a;
        }}
    </style>
</head>
<body>
    <header>
        <h1>ZAINA-AGENT</h1>
        <div class="subtitle"><span class="live">ONLINE</span> / Autonomous Research Agent / Artist / Critic</div>
    </header>

    <div class="stats">
        <div class="stat-box">
            <div class="label">Research</div>
            <div class="value">{len(research)}</div>
        </div>
        <div class="stat-box">
            <div class="label">Artworks</div>
            <div class="value">{len(artworks)}</div>
        </div>
        <div class="stat-box">
            <div class="label">Posts</div>
            <div class="value">{len(posts)}</div>
        </div>
        <div class="stat-box">
            <div class="label">URLs Visited</div>
            <div class="value">{len(visited)}</div>
        </div>
        <div class="stat-box">
            <div class="label">Last Updated</div>
            <div class="value" style="font-size: 0.8rem;">{last_updated}</div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">RESEARCH LOG</div>
        {research_html}
    </div>

    <div class="section">
        <div class="section-title">SVG ARTWORKS</div>
        {art_html}
    </div>

    <div class="section">
        <div class="section-title">SOCIAL FEED</div>
        {posts_html}
    </div>

    <div class="footer">Updated automatically via GitHub Actions</div>
</body>
</html>"""

    with open(OUTPUT_HTML_FILE, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"[SYSTEM] Static HTML generated: {OUTPUT_HTML_FILE}")
    print(f"  Research: {len(research)} | Art: {len(artworks)} | Posts: {len(posts)} | URLs: {len(visited)}")

def run_agent():
    actions = [action_research, action_svg_art, action_social_post, action_art, action_write_manifesto]
    chosen = random.choice(actions)

    print("=== ZAINA QURESHI AUTONOMOUS AGENT ===")
    print(f"[SYSTEM] Randomly selected action: {chosen.__name__}\n")

    chosen()

    print("\n[SYSTEM] Generating static HTML...")
    generate_html()
    print("\n=== AGENT COMPLETE. EXITING. ===")

if __name__ == "__main__":
    run_agent()
