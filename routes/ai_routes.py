"""
AI Routes - Flask blueprint for AI features
FIXED VERSION - Better error handling
"""
from flask import Blueprint, request, jsonify
from services.investigation_service import InvestigationService
from datetime import datetime

# Create blueprint
ai_bp = Blueprint('ai', __name__, url_prefix='/ai')


def _get_primary_ai_service():
    """Return Gemini when available, otherwise fall back to Mistral."""
    try:
        from services.gemini_ai_service import get_gemini_ai_service
        return get_gemini_ai_service(), 'gemini'
    except ValueError:
        try:
            from services.mistral_ai_service import get_mistral_ai_service
            return get_mistral_ai_service(), 'mistral'
        except ValueError:
            raise
    except Exception as gemini_error:
        try:
            from services.mistral_ai_service import get_mistral_ai_service
            return get_mistral_ai_service(), 'mistral'
        except Exception:
            raise gemini_error


def _get_secondary_ai_service(primary_provider: str):
    """Return the non-primary AI service for fallback use."""
    if primary_provider == 'gemini':
        from services.mistral_ai_service import get_mistral_ai_service
        return get_mistral_ai_service(), 'mistral'

    from services.gemini_ai_service import get_gemini_ai_service
    return get_gemini_ai_service(), 'gemini'


def _normalize_threat_level(level: str) -> str:
    """Map AI output to values accepted by the database constraint."""
    allowed_levels = {'critical', 'high', 'medium', 'low', 'safe'}
    normalized = (level or '').strip().lower()
    return normalized if normalized in allowed_levels else 'medium'

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
        
        # Prefer Gemini, fall back to Mistral if Gemini is unavailable.
        try:
            ai_service, provider = _get_primary_ai_service()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'AI service not configured. Please set GEMINI_API_KEY or MISTRAL_API_KEY in .env file.'
            }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'AI service error: {str(e)}'
            }), 500
        
        # Generate AI response, retrying with the backup provider if needed.
        try:
            ai_response = ai_service.chat(
                investigation_data=investigation,
                user_message=user_message,
                chat_history=[]  # We'll add chat history later
            )
        except Exception:
            fallback_service, fallback_provider = _get_secondary_ai_service(provider)
            ai_response = fallback_service.chat(
                investigation_data=investigation,
                user_message=user_message,
                chat_history=[]
            )
            provider = fallback_provider
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'provider': provider,
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
        
        # Get AI service with error handling
        try:
            ai_service, provider = _get_primary_ai_service()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'AI service not configured. Please set GEMINI_API_KEY or MISTRAL_API_KEY in .env file.'
            }), 500
        
        # Generate summary, retrying with the backup provider if needed.
        try:
            summary = ai_service.analyze_investigation(
                investigation=investigation,
                results=results
            )
        except Exception:
            fallback_service, fallback_provider = _get_secondary_ai_service(provider)
            summary = fallback_service.analyze_investigation(
                investigation=investigation,
                results=results
            )
            provider = fallback_provider

        summary['overall_threat'] = _normalize_threat_level(summary.get('overall_threat'))

        persisted_summary = InvestigationService.save_investigation_analysis(
            investigation_id=investigation_id,
            summary=summary
        )

        analyzed_at = (
            persisted_summary.get('created_at')
            if persisted_summary else
            datetime.now().isoformat()
        )
        
        return jsonify({
            'success': True,
            'summary': summary,
            'total_results': len(results),
            'provider': provider,
            'analyzed_at': analyzed_at
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
    # Check if Gemini is configured
    try:
        from services.gemini_ai_service import get_gemini_ai_service
        get_gemini_ai_service()
        gemini_status = "✅ Connected"
    except ValueError:
        gemini_status = "❌ API key not configured"
    except Exception as e:
        gemini_status = f"❌ Error: {str(e)}"

    try:
        from services.mistral_ai_service import get_mistral_ai_service
        get_mistral_ai_service()
        mistral_status = "✅ Connected"
    except ValueError:
        mistral_status = "❌ API key not configured"
    except Exception as e:
        mistral_status = f"❌ Error: {str(e)}"
    
    return jsonify({
        'success': True,
        'message': 'AI routes are working!',
        'gemini_status': gemini_status,
        'mistral_status': mistral_status,
        'endpoints': [
            '/ai/chat',
            '/ai/guide-chat',
            '/ai/analyze/<investigation_id>',
            '/ai/test'
        ]
    })


@ai_bp.route('/guide-chat', methods=['POST'])
def guide_chat():
    """Landing assistant chat for platform/tool guidance."""
    try:
        data = request.get_json() or {}
        user_message = (data.get('message') or '').strip()
        chat_history = data.get('chat_history') or []

        if not user_message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400

        try:
            from services.mistral_guide_service import get_mistral_guide_service
            ai_service = get_mistral_guide_service()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Guide assistant not configured. Please set MISTRAL_API_KEY in .env file.'
            }), 500

        ai_response = ai_service.chat(user_message=user_message, chat_history=chat_history)

        return jsonify({
            'success': True,
            'response': ai_response,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"❌ Guide Chat error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
