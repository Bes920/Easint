"""
Test Mistral AI Connection - FIXED
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    # Correct import for Mistral SDK
    from mistralai.client import MistralClient
    from mistralai.models.chat_completion import ChatMessage
    
    # Get API key
    api_key = os.getenv('MISTRAL_API_KEY')
    
    if not api_key:
        print("❌ MISTRAL_API_KEY not found in .env file")
        print("Add this line to your .env file:")
        print("MISTRAL_API_KEY=your-key-here")
        exit(1)
    
    print("Testing Mistral AI connection...")
    
    # Initialize client
    client = MistralClient(api_key=api_key)
    
    # Test API call
    messages = [
        ChatMessage(role="user", content="Say 'Hello Easint!' in one sentence.")
    ]
    
    response = client.chat(
        model="mistral-small-latest",
        messages=messages
    )
    
    print("✅ Mistral AI works!")
    print(f"Response: {response.choices[0].message.content}")
    print("\n🎉 Ready to build AI features!")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\nTry reinstalling:")
    print("pip uninstall mistralai -y")
    print("pip install mistralai --break-system-packages")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check your API key is correct")
    print("2. Verify you have internet connection")
    print("3. Make sure you have free credits in your Mistral account")
    print("4. Try: pip install --upgrade mistralai --break-system-packages")