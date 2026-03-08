"""
Test Supabase Integration
"""
from services.investigation_service import InvestigationService
from services.chat_service import ChatService
import uuid

def test_investigations():
    """Test investigation operations"""
    print("\n🧪 Testing Investigation Operations...")
    
    # For testing, use a dummy user ID
    test_user_id = str(uuid.uuid4())
    
    # Create investigation
    print("1. Creating investigation...")
    investigation = InvestigationService.create_investigation(
        user_id=test_user_id,
        name="Test Phishing Investigation",
        description="Testing Supabase integration"
    )
    print(f"✅ Created: {investigation['id']}")
    
    # Add a result
    print("\n2. Adding investigation result...")
    result = InvestigationService.add_investigation_result(
        investigation_id=investigation['id'],
        tool_name="ip-checker",
        target="8.8.8.8",
        result_data={
            "ip": "8.8.8.8",
            "country": "US",
            "is_malicious": False
        },
        threat_level="safe"
    )
    print(f"✅ Added result: {result['id']}")
    
    # Get investigation with results
    print("\n3. Fetching investigation with results...")
    full_investigation = InvestigationService.get_investigation_with_results(
        investigation['id']
    )
    print(f"✅ Investigation: {full_investigation['name']}")
    print(f"✅ Results count: {full_investigation['result_count']}")
    
    # Clean up
    print("\n4. Cleaning up test data...")
    InvestigationService.delete_investigation(investigation['id'])
    print("✅ Test data deleted")
    
    print("\n✅ All investigation tests passed!")

def test_chat():
    """Test chat operations"""
    print("\n🧪 Testing Chat Operations...")
    
    test_user_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    
    # Save chat message
    print("1. Saving chat message...")
    message = ChatService.save_chat_message(
        user_id=test_user_id,
        session_id=session_id,
        user_message="How do I check an IP address?",
        bot_response="You can use the IP Reputation tool..."
    )
    print(f"✅ Message saved: {message['id']}")
    
    # Get session history
    print("\n2. Fetching session history...")
    history = ChatService.get_session_history(session_id)
    print(f"✅ Found {len(history)} messages")
    
    print("\n✅ All chat tests passed!")

if __name__ == "__main__":
    print("=" * 60)
    print("EASINT - SUPABASE INTEGRATION TEST")
    print("=" * 60)
    
    try:
        test_investigations()
        test_chat()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED! Supabase is ready!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("Check your .env file and Supabase setup")