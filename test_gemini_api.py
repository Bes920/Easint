"""
Test Gemini API Connection
Run this to verify Gemini works before integrating
"""
import os
from typing import Iterable
from dotenv import load_dotenv

load_dotenv()

PREFERRED_MODELS = [
    'models/gemini-2.5-flash',
    'models/gemini-2.5-pro',
    'models/gemini-2.5-flash-preview',
    'models/gemini-2.0-flash',
    'models/gemini-2.0-flash-exp',
]


def select_model_name(candidate_names: Iterable[str]) -> str | None:
    """Return a preferred model name that is visible to the API key."""
    names = list(candidate_names)
    for preferred in PREFERRED_MODELS:
        if preferred in names:
            return preferred

    return names[0] if names else None


try:
    from google import genai

    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    print("Testing Gemini API...")

    pager = client.models.list(config={'page_size': 25})
    model_names = [model.name for model in pager.page]
    print(f"Available models (first {len(model_names)}):\n  " + "\n  ".join(model_names))

    model_name = select_model_name(model_names)
    if not model_name:
        raise RuntimeError("No models returned from the Gemini API.")

    print(f"Using model: {model_name}")
    response = client.models.generate_content(
        model=model_name,
        contents='Say "Hello from Gemini!" in one sentence.'
    )

    print("✅ Gemini API works!")
    print(f"Response: {response.text}")
    print("\n🎉 Ready to build AI features!")

except ImportError:
    print("❌ google-genai not installed")
    print("Run: pip install google-genai --break-system-packages")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check GEMINI_API_KEY in .env file")
    print("2. Verify API key is correct")
    print("3. Check internet connection")
