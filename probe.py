import os
from google import genai

def probe_zaina():
    key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=key, http_options={'api_version': 'v1'})
    
    print("--- ZAINA DIAGNOSTICS ---")
    try:
        print("Fetching available models...")
        for model in client.models.list():
            print(f"Found: {model.name}")
    except Exception as e:
        print(f"Diagnostic Failure: {e}")

if __name__ == "__main__":
    probe_zaina()
