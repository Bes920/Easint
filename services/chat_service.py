"""
Chat Service - Database operations for AI chatbot
"""
from config.supabase_config import get_supabase_client
from typing import List, Dict
import uuid

supabase = get_supabase_client()

class ChatService:
    """Handle all chat-related database operations"""
    
    @staticmethod
    def save_chat_message(user_id: str, session_id: str, user_message: str, 
                         bot_response: str, investigation_id: str = None) -> Dict:
        """
        Save a chat message exchange
        
        Args:
            user_id: User UUID
            session_id: Chat session UUID
            user_message: User's message
            bot_response: Bot's response
            investigation_id: Optional investigation UUID
            
        Returns:
            Dict: Saved chat message
        """
        try:
            data = {
                'user_id': user_id,
                'session_id': session_id,
                'user_message': user_message,
                'bot_response': bot_response,
                'investigation_id': investigation_id
            }
            
            result = supabase.table('chat_history').insert(data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error saving chat message: {e}")
            raise
    
    @staticmethod
    def get_session_history(session_id: str, limit: int = 50) -> List[Dict]:
        """
        Get chat history for a session
        
        Args:
            session_id: Chat session UUID
            limit: Maximum messages to return
            
        Returns:
            List[Dict]: List of messages
        """
        try:
            result = supabase.table('chat_history')\
                .select('*')\
                .eq('session_id', session_id)\
                .order('created_at', desc=False)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error fetching chat history: {e}")
            return []
    
    @staticmethod
    def get_user_chat_history(user_id: str, limit: int = 100) -> List[Dict]:
        """
        Get all chat history for a user
        
        Args:
            user_id: User UUID
            limit: Maximum messages to return
            
        Returns:
            List[Dict]: List of messages
        """
        try:
            result = supabase.table('chat_history')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error fetching user chat history: {e}")
            return []