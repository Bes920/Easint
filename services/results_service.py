"""
Results Service - Auto-save OSINT tool results to database
"""
from config.supabase_config import get_supabase_client
from services.investigation_service import InvestigationService
from typing import Dict, Optional
import uuid
from datetime import datetime

supabase = get_supabase_client()

class ResultsService:
    """Handle automatic saving of OSINT tool results"""
    
    # Default investigation for auto-saved results (if none specified)
    DEFAULT_INVESTIGATION_NAME = "Auto-saved Results"
    
    @staticmethod
    def get_or_create_default_investigation() -> str:
        """
        Get or create a default investigation for auto-saved results
        
        Returns:
            str: Investigation ID
        """
        try:
            # Try to find existing default investigation
            result = supabase.table('investigations')\
                .select('id')\
                .eq('name', ResultsService.DEFAULT_INVESTIGATION_NAME)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]['id']
            
            # Create new default investigation
            investigation = InvestigationService.create_investigation(
                user_id=None,  # No user required (for now)
                name=ResultsService.DEFAULT_INVESTIGATION_NAME,
                description="Automatically saved tool results"
            )
            return investigation['id']
            
        except Exception as e:
            print(f"Error getting/creating default investigation: {e}")
            # Fallback: create investigation with unique name
            investigation = InvestigationService.create_investigation(
                user_id=None,
                name=f"{ResultsService.DEFAULT_INVESTIGATION_NAME} - {datetime.now().strftime('%Y-%m-%d')}",
                description="Auto-saved results"
            )
            return investigation['id']
    
    @staticmethod
    def save_tool_result(
        tool_name: str,
        target: str,
        result_data: Dict,
        investigation_id: Optional[str] = None,
        threat_level: str = 'low'
    ) -> Optional[Dict]:
        """
        Save a tool result to the database
        
        Args:
            tool_name: Name of the OSINT tool (e.g., 'ip-checker', 'email-breach')
            target: What was investigated (e.g., '8.8.8.8', 'user@example.com')
            result_data: The complete result from the tool (as dict)
            investigation_id: Optional investigation ID (creates default if not provided)
            threat_level: 'safe', 'low', 'medium', 'high', 'critical'
            
        Returns:
            Dict: Saved result or None if failed
        """
        try:
            # Get or create investigation if not provided
            if not investigation_id:
                investigation_id = ResultsService.get_or_create_default_investigation()
            
            # Save the result
            result = InvestigationService.add_investigation_result(
                investigation_id=investigation_id,
                tool_name=tool_name,
                target=target,
                result_data=result_data,
                threat_level=threat_level
            )
            
            print(f"✅ Auto-saved: {tool_name} result for {target}")
            return result
            
        except Exception as e:
            print(f"⚠️ Failed to auto-save {tool_name} result: {e}")
            # Don't crash the app if save fails
            return None
    
    @staticmethod
    def determine_threat_level(result_data: Dict, tool_name: str) -> str:
        """
        Automatically determine threat level based on result data
        
        Args:
            result_data: Tool result data
            tool_name: Name of the tool
            
        Returns:
            str: Threat level ('safe', 'low', 'medium', 'high', 'critical')
        """
        # IP Reputation
        if tool_name in ['ip-checker', 'check-ip']:
            if result_data.get('abuseipdb', {}).get('abuse_score', 0) > 75:
                return 'critical'
            elif result_data.get('abuseipdb', {}).get('abuse_score', 0) > 50:
                return 'high'
            elif result_data.get('abuseipdb', {}).get('abuse_score', 0) > 25:
                return 'medium'
            elif result_data.get('virustotal', {}).get('detections', 0) > 0:
                return 'medium'
            else:
                return 'safe'
        
        # Email Breach
        elif tool_name in ['email-breach', 'email-osint']:
            if result_data.get('breached'):
                return 'high'
            else:
                return 'safe'
        
        # File Hash
        elif tool_name in ['hash-checker', 'file-upload']:
            if result_data.get('virustotal', {}).get('is_malicious'):
                return 'critical'
            elif result_data.get('virustotal', {}).get('detections', 0) > 0:
                return 'high'
            else:
                return 'safe'
        
        # Default
        else:
            return 'low'