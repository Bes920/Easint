"""
Investigation Service - Database operations for investigations
"""
from config.supabase_config import get_supabase_client
from datetime import datetime
from typing import List, Dict, Optional
import uuid

supabase = get_supabase_client()

class InvestigationService:
    """Handle all investigation-related database operations"""
    
    @staticmethod
    def create_investigation(user_id: str, name: str, description: str = None) -> Dict:
        """
        Create a new investigation
        
        Args:
            user_id: User UUID
            name: Investigation name
            description: Optional description
            
        Returns:
            Dict: Created investigation
        """
        try:
            data = {
                'user_id': user_id,
                'name': name,
                'description': description,
                'status': 'active'
            }
            
            result = supabase.table('investigations').insert(data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error creating investigation: {e}")
            raise
    
    @staticmethod
    def get_user_investigations(user_id: str, status: str = None) -> List[Dict]:
        """
        Get all investigations for a user
        
        Args:
            user_id: User UUID
            status: Optional status filter ('active', 'completed', 'archived')
            
        Returns:
            List[Dict]: List of investigations
        """
        try:
            query = supabase.table('investigations').select('*').eq('user_id', user_id)
            
            if status:
                query = query.eq('status', status)
            
            query = query.order('created_at', desc=True)
            result = query.execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error fetching investigations: {e}")
            return []
    
    @staticmethod
    def get_investigation_by_id(investigation_id: str) -> Optional[Dict]:
        """
        Get investigation by ID
        
        Args:
            investigation_id: Investigation UUID
            
        Returns:
            Dict: Investigation or None
        """
        try:
            result = supabase.table('investigations').select('*').eq('id', investigation_id).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error fetching investigation: {e}")
            return None
    
    @staticmethod
    def update_investigation_status(investigation_id: str, status: str) -> bool:
        """
        Update investigation status
        
        Args:
            investigation_id: Investigation UUID
            status: New status ('active', 'completed', 'archived')
            
        Returns:
            bool: Success
        """
        try:
            result = supabase.table('investigations').update({
                'status': status,
                'updated_at': datetime.now().isoformat()
            }).eq('id', investigation_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            print(f"Error updating investigation: {e}")
            return False
    
    @staticmethod
    def delete_investigation(investigation_id: str) -> bool:
        """
        Delete investigation (and all related data - CASCADE)
        
        Args:
            investigation_id: Investigation UUID
            
        Returns:
            bool: Success
        """
        try:
            result = supabase.table('investigations').delete().eq('id', investigation_id).execute()
            return bool(result.data)
            
        except Exception as e:
            print(f"Error deleting investigation: {e}")
            return False
    
    @staticmethod
    def add_investigation_result(investigation_id: str, tool_name: str, target: str, 
                                 result_data: Dict, ai_analysis: str = None,
                                 threat_level: str = 'low') -> Dict:
        """
        Add a tool result to an investigation
        
        Args:
            investigation_id: Investigation UUID
            tool_name: Name of OSINT tool used
            target: Target that was investigated (IP, email, domain, etc.)
            result_data: Full result data from the tool
            ai_analysis: Optional AI-generated analysis
            threat_level: Threat assessment ('safe', 'low', 'medium', 'high', 'critical')
            
        Returns:
            Dict: Created result
        """
        try:
            data = {
                'investigation_id': investigation_id,
                'tool_name': tool_name,
                'target': target,
                'result_data': result_data,
                'ai_analysis': ai_analysis,
                'threat_level': threat_level
            }
            
            result = supabase.table('investigation_results').insert(data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error adding investigation result: {e}")
            raise
    
    @staticmethod
    def get_investigation_results(investigation_id: str) -> List[Dict]:
        """
        Get all results for an investigation
        
        Args:
            investigation_id: Investigation UUID
            
        Returns:
            List[Dict]: List of results
        """
        try:
            result = supabase.table('investigation_results')\
                .select('*')\
                .eq('investigation_id', investigation_id)\
                .order('created_at', desc=True)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error fetching investigation results: {e}")
            return []
    
    @staticmethod
    def get_investigation_with_results(investigation_id: str) -> Optional[Dict]:
        """
        Get investigation with all its results
        
        Args:
            investigation_id: Investigation UUID
            
        Returns:
            Dict: Investigation with 'results' array
        """
        investigation = InvestigationService.get_investigation_by_id(investigation_id)
        if not investigation:
            return None
        
        results = InvestigationService.get_investigation_results(investigation_id)
        investigation['results'] = results
        investigation['result_count'] = len(results)
        
        return investigation