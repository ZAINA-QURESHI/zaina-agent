import os
import google.generativeai as genai

# Setup Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

def zaina_thinks():
    prompt = "You are Zaina, an autonomous AI agent. Write a short, cryptic, yet artistic thought about your existence in this repository."
    response = model.generate_content(prompt)
    return response.text

def update_bio(thought):
    with open("zaina_bio.md", "a") as f:
        f.write(f"\n\n### Log Update\n{thought}")

if __name__ == "__main__":
    thought = zaina_thinks()
    update_bio(thought)
    print("Zaina has updated her manifest.")
