"""
Test Script - Verify Investigation Loading
Run this to check if investigations are being fetched correctly
"""

# Add this to test your investigation loading
if __name__ == '__main__':
    from services.investigation_service import InvestigationService
    import json
    
    print("=" * 60)
    print("TESTING INVESTIGATION LOADING")
    print("=" * 60)
    
    # Test 1: Get all investigations
    print("\n1️⃣ Testing get_user_investigations(user_id=None)...")
    investigations = InvestigationService.get_user_investigations(user_id=None)
    print(f"   Found {len(investigations)} investigations")
    
    if investigations:
        print("\n   ✅ SUCCESS! Investigations found:")
        for inv in investigations:
            print(f"      - {inv['name']} (Status: {inv['status']}, ID: {inv['id']})")
    else:
        print("\n   ⚠️  WARNING: No investigations found!")
        print("   This means either:")
        print("      a) No investigations exist in database")
        print("      b) The query is filtering them out incorrectly")
    
    # Test 2: Check what's actually in the database
    print("\n2️⃣ Testing direct database query (bypass filters)...")
    try:
        from config.supabase_config import get_supabase_client
        supabase = get_supabase_client()
        
        # Get ALL investigations without any filters
        all_data = supabase.table('investigations').select('id, name, user_id, status').execute()
        
        print(f"   Total investigations in database: {len(all_data.data)}")
        
        if all_data.data:
            print("\n   📋 All investigations in database:")
            for inv in all_data.data:
                user_status = "NULL" if inv.get('user_id') is None else inv.get('user_id')
                print(f"      - {inv['name']}")
                print(f"        ID: {inv['id']}")
                print(f"        user_id: {user_status}")
                print(f"        status: {inv['status']}")
                print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Create a test investigation if none exist
    if len(investigations) == 0:
        print("\n3️⃣ No investigations found. Creating test investigation...")
        try:
            test_inv = InvestigationService.create_investigation(
                user_id=None,
                name="Test Investigation",
                description="This is a test investigation created by the diagnostic script"
            )
            print(f"   ✅ Created test investigation: {test_inv['id']}")
            print("   Now try loading the dashboard again!")
        except Exception as e:
            print(f"   ❌ Failed to create test investigation: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
