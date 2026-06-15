"""
Mistral AI Service for EASINT Platform
Provides backup AI-powered analysis and chat for OSINT investigations.
"""
import os
from typing import Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()


class MistralAIService:
    """Service for AI-powered analysis using Mistral."""

    def __init__(self):
        api_key = os.getenv('MISTRAL_API_KEY')
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")

        self.api_key = api_key
        self.model = os.getenv('MISTRAL_MODEL', 'mistral-small-latest')
        self.url = 'https://api.mistral.ai/v1/chat/completions'

    def chat(self, investigation_data: Dict, user_message: str, chat_history: List[Dict] = None) -> str:
        try:
            context = self._build_investigation_context(investigation_data)

            system_prompt = f"""You are an expert OSINT (Open-Source Intelligence) analyst assistant for the EASINT platform.

INVESTIGATION CONTEXT:
{context}

Your role:
- Answer questions about the investigation results
- Provide insights and correlations
- Assess threat levels
- Suggest next steps
- Be concise and professional

Always base your answers on the actual data provided.
Use plain ASCII only.
Prefer short paragraphs and bullet points with "- ".
Avoid fancy punctuation, em dashes, and long prose."""

            messages = [{'role': 'system', 'content': system_prompt}]
            if chat_history:
                for msg in chat_history[-5:]:
                    user_text = (msg.get('user_message') or '').strip()
                    bot_text = (msg.get('bot_response') or '').strip()
                    if user_text:
                        messages.append({'role': 'user', 'content': user_text})
                    if bot_text:
                        messages.append({'role': 'assistant', 'content': bot_text})

            messages.append({'role': 'user', 'content': user_message})

            response = self._post_chat(messages)
            return response
        except Exception as e:
            print(f"❌ Mistral chat error: {e}")
            return "I apologize, but I encountered an error processing your question. Please try rephrasing it."

    def analyze_result(self, tool_name: str, target: str, result_data: Dict) -> Dict:
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

            analysis_text = self._post_chat([
                {'role': 'system', 'content': 'You are a helpful OSINT analysis assistant.'},
                {'role': 'user', 'content': prompt},
            ])

            return {
                'analysis': self._extract_section(analysis_text, 'ANALYSIS') or analysis_text[:500],
                'threat_level': self._extract_threat_level(analysis_text),
                'findings': self._extract_list(analysis_text, 'FINDINGS'),
                'recommendations': self._extract_list(analysis_text, 'RECOMMENDATIONS'),
                'full_text': analysis_text
            }
        except Exception as e:
            print(f"❌ Mistral analysis error: {e}")
            return {
                'analysis': 'Analysis unavailable at this time.',
                'threat_level': 'unknown',
                'findings': [],
                'recommendations': [],
                'full_text': str(e)
            }

    def analyze_investigation(self, investigation: Dict, results: List[Dict]) -> Dict:
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

            summary_text = self._post_chat([
                {'role': 'system', 'content': 'You are a helpful OSINT analysis assistant.'},
                {'role': 'user', 'content': prompt},
            ])

            return {
                'summary': self._extract_section(summary_text, 'SUMMARY') or summary_text[:300],
                'overall_threat': self._extract_threat_level(summary_text),
                'insights': self._extract_section(summary_text, 'INSIGHTS'),
                'correlations': self._extract_section(summary_text, 'CORRELATIONS'),
                'actions': self._extract_section(summary_text, 'ACTIONS'),
                'full_text': summary_text
            }
        except Exception as e:
            print(f"❌ Mistral investigation analysis error: {e}")
            return {
                'summary': 'Investigation summary unavailable.',
                'overall_threat': 'unknown',
                'insights': '',
                'correlations': '',
                'actions': '',
                'full_text': str(e)
            }

    def _post_chat(self, messages: List[Dict[str, str]]) -> str:
        response = requests.post(
            self.url,
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': self.model,
                'temperature': 0.2,
                'messages': messages,
            },
            timeout=30,
        )

        if response.status_code >= 400:
            raise RuntimeError(f"Mistral API error ({response.status_code}): {response.text}")

        data = response.json()
        choices = data.get('choices', [])
        if not choices:
            raise RuntimeError('Mistral response did not include choices')

        content = choices[0].get('message', {}).get('content', '')
        if isinstance(content, list):
            content = '\n'.join(
                part.get('text', '') for part in content if isinstance(part, dict)
            )

        return self._normalize_text(content or '').strip()

    def _build_investigation_context(self, investigation_data: Dict) -> str:
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
        if not data:
            return 'No data available'

        formatted = ''
        for key, value in list(data.items())[:10]:
            formatted += f"{key}: {str(value)[:200]}\n"

        return formatted[:max_length]

    def _extract_threat_level(self, text: str) -> str:
        text_lower = text.lower()
        if 'critical' in text_lower:
            return 'critical'
        if 'high' in text_lower:
            return 'high'
        if 'medium' in text_lower:
            return 'medium'
        if 'low' in text_lower:
            return 'low'
        if 'safe' in text_lower:
            return 'safe'
        return 'medium'

    def _extract_section(self, text: str, section_name: str) -> str:
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
        section = self._extract_section(text, section_name)
        if not section:
            return []

        items = []
        for line in section.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                clean = line.lstrip('-•0123456789. ')
                if clean:
                    items.append(clean)

        return items

    def _normalize_text(self, text: str) -> str:
        """Normalize Mistral output for UI and PDF consumption."""
        replacements = {
            '\u2013': '-',
            '\u2014': '-',
            '\u2022': '-',
            '\u2018': "'",
            '\u2019': "'",
            '\u201c': '"',
            '\u201d': '"',
        }
        normalized = text
        for source, target in replacements.items():
            normalized = normalized.replace(source, target)
        return normalized.encode('ascii', errors='replace').decode('ascii')

    def _summarize_results(self, results: List[Dict]) -> str:
        if not results:
            return "No results available"

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


_ai_service = None


def get_mistral_ai_service() -> MistralAIService:
    global _ai_service
    if _ai_service is None:
        _ai_service = MistralAIService()
    return _ai_service
