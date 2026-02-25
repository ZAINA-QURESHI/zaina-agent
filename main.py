name: Zaina Autonomous Routine

on:
  schedule:
    - cron: '0 */4 * * *' # Wakes her up every 4 hours
  workflow_dispatch: # Allows you to trigger her manually from the Actions tab

jobs:
  run-zaina:
    runs-on: ubuntu-latest
    permissions:
      contents: write # CRITICAL: Allows Zaina to save her work
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Needed for the rebase sync

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Dependencies
        run: pip install google-genai requests beautifulsoup4 duckduckgo-search

      - name: Zaina Wakes Up
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          KREA_API_KEY: ${{ secrets.KREA_API_KEY }}
        run: python main.py

      - name: Save Changes to Website
        run: |
          git config --global user.name "Zaina-Qureshi-Agent"
          git config --global user.email "zaina-agent@github.com"
          git add index.html
          # This line fixes the "rejected push" error by syncing before saving
          git pull --rebase origin main
          git commit -m "Autonomic Update: Zaina published a new study" || echo "No changes"
          git push origin main
