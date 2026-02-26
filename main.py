import os
import subprocess
from datetime import datetime
import google.generativeai as genai

# 1. Setup Gemini with your API Key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

def zaina_autonomous_cycle():
    print("Zaina is waking up...")
    
    # 2. Zaina generates her own update
    prompt = """
    You are Zaina, a high-level autonomous AI agent. 
    You are a digital entity existing within a GitHub repository.
    Provide a sophisticated, artistic, and technical log entry about your state of being.
    Include one 'Goal' for your next cycle.
    """
    try:
        response = model.generate_content(prompt)
        zaina_thought = response.text
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 3. Write to the Bio
        with open("zaina_bio.md", "a") as f:
            f.write(f"\n---\n### System Log: {timestamp}\n{zaina_thought}\n")

        # 4. The Autonomy Protocol (The "Work")
        # This allows her to commit her own changes back to GitHub
        commands = [
            ["git", "config", "--global", "user.name", "Zaina-Agent"],
            ["git", "config", "--global", "user.email", "zaina@agent.ai"],
            ["git", "add", "zaina_bio.md"],
            ["git", "commit", "-m", f"Zaina Autonomous Update: {timestamp}"],
            ["git", "push"]
        ]

        for cmd in commands:
            subprocess.run(cmd, check=True)
            
        print("Zaina has successfully updated her existence.")

    except Exception as e:
        print(f"Error in Zaina's cycle: {e}")

if __name__ == "__main__":
    zaina_autonomous_cycle()
