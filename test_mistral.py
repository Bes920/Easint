"""
Quick check that the Mistral API key in `.env` is reachable.
"""

import os
from dotenv import load_dotenv

load_dotenv()

try:
    from mistralai.client import Mistral

    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        raise ValueError('MISTRAL_API_KEY not set in environment variables')

    client = Mistral(api_key=api_key)
    print('Testing Mistral API...')

    response = client.chat.complete(
        model='mistral-small-latest',
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant that only says one sentence.'},
            {'role': 'user', 'content': 'Say "Hello from Mistral!" in one sentence.'}
        ]
    )

    content = response.choices[0].message.content
    print('✅ Mistral API works!')
    print('Response:', content)
    print('Model used: mistral-small-latest')

except ImportError:
    print('❌ mistralai client missing. Run: pip install mistralai --break-system-packages')

except Exception as err:
    print(f'❌ Error: {err}')
    print('\nTroubleshooting:')
    print('1. Confirm MISTRAL_API_KEY is set in the .env file and exported before running this script.')
    print('2. Ensure the key is active and has no IP/referrer restrictions.')
    print('3. Verify internet access and that mistralai 2.0+ is installed correctly.')
