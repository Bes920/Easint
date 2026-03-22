"""
Gemini AI Service for EASINT Platform
Provides AI-powered analysis and chat for OSINT investigations

Location: services/gemini_ai_service.py
"""
import os
from typing import Dict, List, Optional
from google import genai
from dotenv import load_dotenv

load_dotenv()

class GeminiAIService:
    """Service for AI-powered analysis using Google Gemini"""
    
    def __init__(self):
        """Initialize Gemini client"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-flash-latest"  # Fast, free model
    
    def chat(self, investigation_data: Dict, user_message: str, chat_history: List[Dict] = None) -> str:
        """
        Chat with AI about investigation results
        
        Args:
            investigation_data: Investigation details and results
            user_message: User's question
            chat_history: Previous chat messages (optional)
        
        Returns:
            AI response as string
        """
        try:
            # Build context from investigation
            context = self._build_investigation_context(investigation_data)
            
            # Build prompt
            system_prompt = f"""You are an expert OSINT (Open-Source Intelligence) analyst assistant for the EASINT platform.

INVESTIGATION CONTEXT:
{context}

Your role:
- Answer questions about the investigation results
- Provide insights and correlations
- Assess threat levels
- Suggest next steps
- Be concise and professional

Always base your answers on the actual data provided."""
            
            # Add chat history if provided
            conversation = system_prompt + "\n\n"
            if chat_history:
                for msg in chat_history[-5:]:  # Last 5 messages
                    conversation += f"User: {msg.get('user_message', '')}\n"
                    conversation += f"Assistant: {msg.get('bot_response', '')}\n"
            
            # Add current question
            conversation += f"User: {user_message}\nAssistant:"
            
            # Generate response
            response = self.client.models.generate_content(
                model=self.model,
                contents=conversation
            )
            
            return response.text
            
        except Exception as e:
            print(f"❌ Chat error: {e}")
            return f"I apologize, but I encountered an error processing your question. Please try rephrasing it."
    
    def analyze_result(self, tool_name: str, target: str, result_data: Dict) -> Dict:
        """
        Analyze a single OSINT tool result
        
        Args:
            tool_name: Name of the tool used
            target: Target that was analyzed
            result_data: Tool output data
        
        Returns:
            Dictionary with analysis, threat_level, and recommendations
        """
        try:
            prompt = f"""Analyze this OSINT tool result and provide a security assessment.

TOOL: {tool_name}
TARGET: {target}
RESULT DATA:
{self._format_result_data(result_data)}

Provide:
1. Brief analysis (2-3 sentences)
2. Threat level (critical/high/medium/low/safe)
3. Key findings (bullet points)
4. Recommendations (if any threats found)

Format your response as:
ANALYSIS: [your analysis]
THREAT: [threat level]
FINDINGS:
- [finding 1]
- [finding 2]
RECOMMENDATIONS:
- [recommendation 1]
- [recommendation 2]"""
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            analysis_text = response.text
            
            # Extract sections
            return {
                'analysis': self._extract_section(analysis_text, 'ANALYSIS') or analysis_text[:500],
                'threat_level': self._extract_threat_level(analysis_text),
                'findings': self._extract_list(analysis_text, 'FINDINGS'),
                'recommendations': self._extract_list(analysis_text, 'RECOMMENDATIONS'),
                'full_text': analysis_text
            }
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return {
                'analysis': 'Analysis unavailable at this time.',
                'threat_level': 'unknown',
                'findings': [],
                'recommendations': [],
                'full_text': str(e)
            }
    
    def analyze_investigation(self, investigation: Dict, results: List[Dict]) -> Dict:
        """
        Generate comprehensive investigation summary
        
        Args:
            investigation: Investigation metadata
            results: List of all investigation results
        
        Returns:
            Dictionary with summary, overall_threat, insights, and actions
        """
        try:
            results_summary = self._summarize_results(results)
            
            prompt = f"""Generate a comprehensive OSINT investigation summary.

INVESTIGATION: {investigation.get('name')}
DESCRIPTION: {investigation.get('description', 'N/A')}
TOTAL RESULTS: {len(results)}

RESULTS BREAKDOWN:
{results_summary}

Provide:
1. Executive Summary (3-4 sentences)
2. Overall Threat Assessment (critical/high/medium/low/safe)
3. Key Insights (3-5 bullet points)
4. Correlations (connections between results)
5. Recommended Actions (prioritized steps)

Format as:
SUMMARY: [executive summary]
THREAT: [overall threat level]
INSIGHTS:
- [insight 1]
- [insight 2]
CORRELATIONS:
- [correlation 1]
ACTIONS:
1. [high priority]
2. [medium priority]"""
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            summary_text = response.text
            
            return {
                'summary': self._extract_section(summary_text, 'SUMMARY') or summary_text[:300],
                'overall_threat': self._extract_threat_level(summary_text),
                'insights': self._extract_section(summary_text, 'INSIGHTS'),
                'correlations': self._extract_section(summary_text, 'CORRELATIONS'),
                'actions': self._extract_section(summary_text, 'ACTIONS'),
                'full_text': summary_text
            }
            
        except Exception as e:
            print(f"❌ Investigation analysis error: {e}")
            return {
                'summary': 'Investigation summary unavailable.',
                'overall_threat': 'unknown',
                'insights': '',
                'correlations': '',
                'actions': '',
                'full_text': str(e)
            }
    
    # ========== HELPER METHODS ==========
    
    def _build_investigation_context(self, investigation_data: Dict) -> str:
        """Build context string from investigation data"""
        inv = investigation_data
        results = inv.get('results', [])
        
        context = f"""
Investigation: {inv.get('name')}
Description: {inv.get('description', 'N/A')}
Status: {inv.get('status')}
Total Results: {len(results)}

Results Summary:
"""
        for i, result in enumerate(results[:10], 1):
            context += f"\n{i}. {result.get('tool_name')} - {result.get('target')}"
            context += f"\n   Threat: {result.get('threat_level', 'N/A')}"
        
        return context
    
    def _format_result_data(self, data: Dict, max_length: int = 1000) -> str:
        """Format result data for AI prompt"""
        if not data:
            return "No data available"
        
        formatted = ""
        for key, value in list(data.items())[:10]:  # Limit to 10 keys
            formatted += f"{key}: {str(value)[:200]}\n"
        
        return formatted[:max_length]
    
    def _extract_threat_level(self, text: str) -> str:
        """Extract threat level from AI response"""
        text_lower = text.lower()
        
        if 'critical' in text_lower:
            return 'critical'
        elif 'high' in text_lower:
            return 'high'
        elif 'medium' in text_lower:
            return 'medium'
        elif 'low' in text_lower:
            return 'low'
        elif 'safe' in text_lower:
            return 'safe'
        else:
            return 'medium'
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a section from formatted AI response"""
        try:
            start_marker = f"{section_name}:"
            if start_marker not in text:
                return ""
            
            start = text.index(start_marker) + len(start_marker)
            remaining = text[start:]
            
            next_markers = ['THREAT:', 'FINDINGS:', 'RECOMMENDATIONS:', 'SUMMARY:', 
                          'INSIGHTS:', 'CORRELATIONS:', 'ACTIONS:']
            end = len(remaining)
            for marker in next_markers:
                if marker in remaining and marker != start_marker:
                    pos = remaining.index(marker)
                    if pos < end:
                        end = pos
            
            return remaining[:end].strip()
            
        except Exception:
            return ""
    
    def _extract_list(self, text: str, section_name: str) -> List[str]:
        """Extract list items from a section"""
        section = self._extract_section(text, section_name)
        if not section:
            return []
        
        items = []
        for line in section.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                # Remove bullet points and numbering
                clean = line.lstrip('-•0123456789. ')
                if clean:
                    items.append(clean)
        
        return items
    
    def _summarize_results(self, results: List[Dict]) -> str:
        """Create a summary of all results"""
        if not results:
            return "No results available"
        
        # Group by tool
        by_tool = {}
        for result in results:
            tool = result.get('tool_name', 'unknown')
            if tool not in by_tool:
                by_tool[tool] = []
            by_tool[tool].append(result)
        
        summary = ""
        for tool, tool_results in by_tool.items():
            threat_counts = {}
            for r in tool_results:
                threat = r.get('threat_level', 'unknown')
                threat_counts[threat] = threat_counts.get(threat, 0) + 1
            
            summary += f"\n{tool}: {len(tool_results)} results - Threats: {dict(threat_counts)}"
        
        return summary


# Singleton instance
_ai_service = None

def get_gemini_ai_service() -> GeminiAIService:
    """Get or create AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = GeminiAIService()
    return _ai_service