"""
AI Routes - Flask blueprint for AI features
Separate from main app.py for clean integration

Location: routes/ai_routes.py (NEW FOLDER)
"""
from flask import Blueprint, request, jsonify
from services.gemini_ai_service import get_gemini_ai_service
from services.investigation_service import InvestigationService
from datetime import datetime

# Create blueprint
ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

@ai_bp.route('/chat', methods=['POST'])
def chat():
    """
    Chat with AI about investigation results
    
    POST /ai/chat
    Body: {
        "investigation_id": "uuid",
        "message": "What's the threat level?"
    }
    
    Returns: {
        "success": true,
        "response": "AI response text"
    }
    """
    try:
        data = request.get_json()
        investigation_id = data.get('investigation_id')
        user_message = data.get('message', '').strip()
        
        if not investigation_id or not user_message:
            return jsonify({
                'success': False,
                'error': 'Investigation ID and message are required'
            }), 400
        
        # Get investigation with results
        investigation = InvestigationService.get_investigation_with_results(investigation_id)
        
        if not investigation:
            return jsonify({
                'success': False,
                'error': 'Investigation not found'
            }), 404
        
        # Get AI service and generate response
        ai_service = get_gemini_ai_service()
        ai_response = ai_service.chat(
            investigation_data=investigation,
            user_message=user_message,
            chat_history=[]  # We'll add chat history later
        )
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ AI Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/analyze/<investigation_id>', methods=['POST'])
def analyze_investigation(investigation_id):
    """
    Generate AI analysis of entire investigation
    
    POST /ai/analyze/<investigation_id>
    
    Returns: {
        "success": true,
        "summary": {...}
    }
    """
    try:
        # Get investigation with results
        investigation = InvestigationService.get_investigation_with_results(investigation_id)
        
        if not investigation:
            return jsonify({
                'success': False,
                'error': 'Investigation not found'
            }), 404
        
        results = investigation.get('results', [])
        
        if not results:
            return jsonify({
                'success': False,
                'error': 'No results to analyze. Run some OSINT tools first.'
            }), 400
        
        # Get AI service and generate summary
        ai_service = get_gemini_ai_service()
        summary = ai_service.analyze_investigation(
            investigation=investigation,
            results=results
        )
        
        return jsonify({
            'success': True,
            'summary': summary,
            'total_results': len(results)
        })
        
    except Exception as e:
        print(f"❌ Investigation Analysis error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify AI routes are registered"""
    return jsonify({
        'success': True,
        'message': 'AI routes are working!',
        'endpoints': [
            '/ai/chat',
            '/ai/analyze/<investigation_id>',
            '/ai/test'
        ]
    })