"""
Supabase Configuration for Easint Platform
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Validate credentials
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Missing Supabase credentials. "
        "Please set SUPABASE_URL and SUPABASE_KEY in your .env file"
    )

# Create Supabase client (singleton)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client() -> Client:
    """
    Get the Supabase client instance
    
    Returns:
        Client: Supabase client
    """
    return supabase

def test_connection():
    """
    Test Supabase connection
    
    Returns:
        bool: True if connection successful
    """
    try:
        # Try to query a table (should return empty if no data)
        result = supabase.table('investigations').select('id').limit(1).execute()
        print("✅ Supabase connection successful!")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

# Test connection on import (optional - remove if you don't want auto-test)
if __name__ == "__main__":
    test_connection()