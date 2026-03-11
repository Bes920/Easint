"""
Investigation Service - FIXED VERSION
Handles investigation CRUD operations with proper NULL user_id handling
"""
from config.supabase_config import get_supabase_client
from typing import Dict, List, Optional
from datetime import datetime

supabase = get_supabase_client()

class InvestigationService:
    """Service for managing investigations"""
    
    @staticmethod
    def create_investigation(
        user_id: Optional[str],
        name: str,
        description: str = "",
        tags: List[str] = None
    ) -> Dict:
        """
        Create a new investigation
        """
        try:
            investigation_data = {
                'user_id': user_id,
                'name': name,
                'description': description,
                'status': 'active',
                'tags': tags or []
            }
            
            result = supabase.table('investigations').insert(investigation_data).execute()
            
            if result.data and len(result.data) > 0:
                print(f"✅ Investigation created: {result.data[0]['id']}")
                return result.data[0]
            else:
                raise Exception("Failed to create investigation")
                
        except Exception as e:
            print(f"❌ Error creating investigation: {e}")
            raise
    
    @staticmethod
    def get_user_investigations(user_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        """
        Get all investigations for a user
        
        ⚠️ FIXED: Now properly handles NULL user_id
        """
        try:
            # Start with base query
            query = supabase.table('investigations').select('*')
            
            # ✅ FIX: Handle NULL user_id properly for Supabase
            if user_id is None:
                # In Supabase/PostgreSQL, we need to check for NULL explicitly
                # Using .is_() doesn't work well, so we'll get ALL and filter in Python
                pass  # Get all investigations
            else:
                query = query.eq('user_id', user_id)
            
            # Filter by status if provided
            if status:
                query = query.eq('status', status)
            
            # Order by newest first
            query = query.order('created_at', desc=True)
            
            # Execute query
            result = query.execute()
            
            # ✅ FIX: Filter for NULL user_id in Python (more reliable)
            if user_id is None and result.data:
                # Filter to only get investigations where user_id is None/NULL
                filtered = [inv for inv in result.data if inv.get('user_id') is None]
                return filtered
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Error fetching investigations: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def get_investigation_by_id(investigation_id: str) -> Optional[Dict]:
        """
        Get a single investigation by ID
        """
        try:
            result = supabase.table('investigations')\
                .select('*')\
                .eq('id', investigation_id)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"❌ Error fetching investigation: {e}")
            return None
    
    @staticmethod
    def update_investigation_status(investigation_id: str, status: str) -> bool:
        """
        Update investigation status
        """
        try:
            result = supabase.table('investigations')\
                .update({'status': status, 'updated_at': datetime.now().isoformat()})\
                .eq('id', investigation_id)\
                .execute()
            
            return result.data is not None and len(result.data) > 0
            
        except Exception as e:
            print(f"❌ Error updating investigation: {e}")
            return False
    
    @staticmethod
    def delete_investigation(investigation_id: str) -> bool:
        """
        Delete an investigation and all its results
        """
        try:
            # First delete all results
            supabase.table('investigation_results')\
                .delete()\
                .eq('investigation_id', investigation_id)\
                .execute()
            
            # Then delete the investigation
            result = supabase.table('investigations')\
                .delete()\
                .eq('id', investigation_id)\
                .execute()
            
            print(f"✅ Deleted investigation: {investigation_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting investigation: {e}")
            return False
    
    @staticmethod
    def add_investigation_result(
        investigation_id: str,
        tool_name: str,
        target: str,
        result_data: Dict,
        ai_analysis: str = None,
        threat_level: str = 'low'
    ) -> Optional[Dict]:
        """
        Add a result to an investigation
        """
        try:
            result_entry = {
                'investigation_id': investigation_id,
                'tool_name': tool_name,
                'target': target,
                'result_data': result_data,
                'ai_analysis': ai_analysis,
                'threat_level': threat_level
            }
            
            result = supabase.table('investigation_results').insert(result_entry).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"❌ Error adding investigation result: {e}")
            return None
    
    @staticmethod
    def get_investigation_results(investigation_id: str) -> List[Dict]:
        """
        Get all results for an investigation
        """
        try:
            result = supabase.table('investigation_results')\
                .select('*')\
                .eq('investigation_id', investigation_id)\
                .order('created_at', desc=True)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Error fetching investigation results: {e}")
            return []
    
    @staticmethod
    def get_investigation_with_results(investigation_id: str) -> Optional[Dict]:
        """
        Get investigation with all its results
        """
        try:
            investigation = InvestigationService.get_investigation_by_id(investigation_id)
            
            if not investigation:
                return None
            
            results = InvestigationService.get_investigation_results(investigation_id)
            investigation['results'] = results
            
            return investigation
            
        except Exception as e:
            print(f"❌ Error fetching investigation with results: {e}")
            return None
