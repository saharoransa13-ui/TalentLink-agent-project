"""Quick test: does the key in .env work with the chosen provider?"""
import os, sys
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env", override=True)
key = os.getenv("OPENAI_API_KEY", "")
base = os.getenv("OPENAI_BASE_URL", "").rstrip("/")
model = os.getenv("OPENAI_MODEL", "")

if not key or key == "PUT_YOUR_KEY_HERE":
    sys.exit("[X] OPENAI_API_KEY is empty in .env")
if not base or not model:
    sys.exit("[X] OPENAI_BASE_URL or OPENAI_MODEL is empty in .env")

print(f"Provider: {base}\nModel:    {model}\nKey:      {key[:6]}...{key[-4:]}")
url = base if base.endswith("/chat/completions") else base + "/chat/completions"
try:
    r = requests.post(url, timeout=30,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": model, "messages": [{"role": "user", "content": "Reply with: OK"}], "max_tokens": 10})
except Exception as e:
    sys.exit(f"[X] Connection error: {e}")
if r.ok:
    print("[OK] Key works! Reply:", r.json()["choices"][0]["message"]["content"].strip())
else:
    print(f"[X] HTTP {r.status_code}: {r.text[:400]}")
    print("401 = wrong key / wrong provider URL, 404 = wrong model name, 429 = quota/credit")
