# Zaina-Agent

## Overview
Autonomous research agent embodying "Zaina Qureshi," a radical anti-imperialist artist and former content moderator. Searches the web for topics related to institutional critique, digital art, and politics. Uses Google Gemini AI to analyze findings, generate SVG artworks, and draft social posts. Generates a static HTML page with all results. Designed to run via GitHub Actions and deploy to GitHub Pages.

## Project Architecture
- `main.py` - Main script: randomly picks one action (research, art, social post), executes it, generates static index.html, then exits
- `index.html` - Generated static page showing all research entries, SVG artworks, and social posts
- `agent_research.md` - Markdown log of all research findings
- `social_feed.txt` - JSONL log of social media posts
- `art_log.txt` - JSONL log of generated artworks
- `svg_art/` - Directory containing generated SVG artwork files
- `visited_urls.txt` - Memory file tracking previously visited URLs

## Three Action Modes (randomly chosen each run)
1. **Research** - DuckDuckGo search, scrape pages, Gemini analysis
2. **SVG Art** - Gemini generates abstract political SVG artwork
3. **Social Post** - Gemini drafts a short critical social media post

## Key Dependencies
- Python 3.11
- `google-genai` - Google Gemini AI client
- `ddgs` - DuckDuckGo search
- `beautifulsoup4` - Web page scraping
- `requests` - HTTP requests

## Configuration
- `GEMINI_API_KEY` - stored in Replit Secrets (or GitHub Secrets for Actions)
- Script runs once per execution (no loop, no server)
- Voice: blunt, exhausted, clinical, ambitious. No em-dashes, no AI filler words.

## Recent Changes
- 2026-02-22: Initial project setup
- 2026-02-22: Added autonomous research agent code
- 2026-02-22: Fixed ddgs dependency, added Flask web server, cleared old URLs
- 2026-02-22: Added real web scraping with BeautifulSoup
- 2026-02-22: Removed Flask, switched to static HTML generation for GitHub Pages deployment
- 2026-02-22: Added 3 action modes (research, SVG art, social posts), random selection per run, beautiful HTML with sections for all content types
