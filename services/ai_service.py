"""
AI Service for EASINT Platform
Uses Mistral AI for AI-powered analysis and chat

Location: services/ai_service.py
"""
import os
from typing import Any, Dict, List, Optional
from mistralai.client import Mistral
from dotenv import load_dotenv

load_dotenv()

class AIService:
    """Service for AI-powered analysis using Mistral AI"""
    
    def __init__(self):
        """Initialize Mistral client"""
        api_key = os.getenv('MISTRAL_API_KEY')
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
        
        self.client = Mistral(api_key=api_key)
        self.model = "mistral-small-latest"  # Fast, free tier model

    def _chat_complete(self, messages: List[Dict]) -> Any:
        """Delegate to the chat completion endpoint with the configured model."""
        return self.client.chat.complete(model=self.model, messages=messages)
    
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
            
            # Build messages for API
            messages = []
            
            # System message with context
            system_content = f"""You are an expert OSINT (Open-Source Intelligence) analyst assistant for the EASINT platform.

INVESTIGATION CONTEXT:
{context}

Your role:
- Answer questions about the investigation results
- Provide insights and correlations
- Assess threat levels
- Suggest next steps
- Be concise and professional

Always base your answers on the actual data provided."""
            
            messages.append({"role": "system", "content": system_content})
            
            # Add chat history if provided
            if chat_history:
                for msg in chat_history[-5:]:  # Last 5 messages for context
                    messages.append({"role": "user", "content": msg.get('user_message', '')})
                    messages.append({"role": "assistant", "content": msg.get('bot_response', '')})
            
            # Add current question
            messages.append({"role": "user", "content": user_message})
            
            # Generate response
            response = self._chat_complete(messages)
            
            return response.choices[0].message.content
            
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
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a cybersecurity analyst specializing in OSINT analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self._chat_complete(messages)
            
            # Parse response
            analysis_text = response.choices[0].message.content
            
            # Extract threat level
            threat_level = self._extract_threat_level(analysis_text)
            
            # Extract sections
            findings = self._extract_section(analysis_text, 'FINDINGS')
            recommendations = self._extract_section(analysis_text, 'RECOMMENDATIONS')
            analysis = self._extract_section(analysis_text, 'ANALYSIS')
            
            return {
                'analysis': analysis or analysis_text[:500],
                'threat_level': threat_level,
                'findings': [f.strip() for f in findings.split('\n') if f.strip()] if findings else [],
                'recommendations': [r.strip() for r in recommendations.split('\n') if r.strip()] if recommendations else [],
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
            Dictionary with summary, overall_threat, key_insights, and recommendations
        """
        try:
            # Build context
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
3. Key Insights (3-5 bullet points of most important findings)
4. Correlations (connections between different results)
5. Recommended Actions (prioritized next steps)

Format as:
SUMMARY: [executive summary]
THREAT: [overall threat level]
INSIGHTS:
- [insight 1]
- [insight 2]
CORRELATIONS:
- [correlation 1]
- [correlation 2]
ACTIONS:
1. [high priority action]
2. [medium priority action]
3. [low priority action]"""
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a senior OSINT analyst creating executive summaries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self._chat_complete(messages)
            
            summary_text = response.choices[0].message.content
            
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
        for i, result in enumerate(results[:10], 1):  # Limit to 10 recent results
            context += f"\n{i}. {result.get('tool_name')} - {result.get('target')}"
            context += f"\n   Threat: {result.get('threat_level', 'N/A')}"
            if result.get('result_data'):
                # Add key data points
                data = result['result_data']
                if isinstance(data, dict):
                    for key in list(data.keys())[:3]:  # First 3 keys
                        context += f"\n   {key}: {str(data[key])[:100]}"
        
        return context
    
    def _format_result_data(self, data: Dict, max_length: int = 1000) -> str:
        """Format result data for AI prompt"""
        if not data:
            return "No data available"
        
        formatted = ""
        for key, value in data.items():
            if isinstance(value, dict):
                formatted += f"\n{key}:\n"
                for k, v in list(value.items())[:5]:  # Limit nested items
                    formatted += f"  {k}: {str(v)[:100]}\n"
            else:
                formatted += f"{key}: {str(value)[:200]}\n"
        
        # Truncate if too long
        return formatted[:max_length]
    
    def _extract_threat_level(self, text: str) -> str:
        """Extract threat level from AI response"""
        text_lower = text.lower()
        
        if 'critical' in text_lower:
            return 'critical'
        elif 'high' in text_lower and 'threat' in text_lower:
            return 'high'
        elif 'medium' in text_lower:
            return 'medium'
        elif 'low' in text_lower:
            return 'low'
        elif 'safe' in text_lower or 'clean' in text_lower:
            return 'safe'
        else:
            return 'medium'  # Default
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a section from formatted AI response"""
        try:
            # Find section
            start_marker = f"{section_name}:"
            if start_marker not in text:
                return ""
            
            # Get text after marker
            start = text.index(start_marker) + len(start_marker)
            remaining = text[start:]
            
            # Find next section or end
            next_markers = ['THREAT:', 'FINDINGS:', 'RECOMMENDATIONS:', 'SUMMARY:', 
                          'INSIGHTS:', 'CORRELATIONS:', 'ACTIONS:']
            end = len(remaining)
            for marker in next_markers:
                if marker in remaining and marker != start_marker:
                    pos = remaining.index(marker)
                    if pos < end:
                        end = pos
            
            section_text = remaining[:end].strip()
            return section_text
            
        except Exception:
            return ""
    
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
        
        # Create summary
        summary = ""
        for tool, tool_results in by_tool.items():
            threat_counts = {}
            for r in tool_results:
                threat = r.get('threat_level', 'unknown')
                threat_counts[threat] = threat_counts.get(threat, 0) + 1
            
            summary += f"\n{tool}: {len(tool_results)} results"
            if threat_counts:
                summary += f" - Threats: {dict(threat_counts)}"
        
        return summary


# Singleton instance
_ai_service = None

def get_ai_service() -> AIService:
    """Get or create AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
