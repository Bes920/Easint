"""
Result Interpretation Service
Generates a user-friendly explanation for each OSINT tool result.
"""
from typing import Dict


class ResultInterpretationService:
    """Create plain-language interpretations for tool results."""

    @staticmethod
    def build_interpretation(tool_name: str, target: str, result_data: Dict) -> str:
        if ResultInterpretationService._is_confirmed_malicious(tool_name, result_data):
            return ResultInterpretationService._malicious_file_interpretation(tool_name, target, result_data)

        try:
            from routes.ai_routes import _get_primary_ai_service

            ai_service, _provider = _get_primary_ai_service()
            analysis = ai_service.analyze_result(tool_name=tool_name, target=target, result_data=result_data)
            text = (analysis.get('analysis') or '').strip()
            if text:
                return ResultInterpretationService._polish_analysis(tool_name, target, result_data, text)
        except Exception as error:
            print(f"⚠️ AI interpretation unavailable for {tool_name}: {error}")

        return ResultInterpretationService._fallback_interpretation(tool_name, target, result_data)

    @staticmethod
    def _is_confirmed_malicious(tool_name: str, result_data: Dict) -> bool:
        tool = (tool_name or '').lower()
        if tool not in {'hash-checker', 'file-upload'}:
            return False

        vt = result_data.get('virustotal', {}) if isinstance(result_data, dict) else {}
        candidates = []
        if isinstance(vt, dict):
            candidates.append(vt)
        if isinstance(result_data, dict):
            candidates.append(result_data)

        for candidate in candidates:
            if candidate.get('is_malicious'):
                return True
            if (candidate.get('detections') or 0) > 0:
                return True
            status = str(candidate.get('status') or candidate.get('malware_status') or candidate.get('result') or '').lower()
            if status in {'malicious', 'suspicious', 'detected'}:
                return True

        return False

    @staticmethod
    def _malicious_file_interpretation(tool_name: str, target: str, result_data: Dict) -> str:
        vt = result_data.get('virustotal', {}) if isinstance(result_data, dict) else {}
        source_data = vt if isinstance(vt, dict) and vt else (result_data if isinstance(result_data, dict) else {})
        detections = source_data.get('detections', 0)
        total = source_data.get('total_scanners', source_data.get('total', 0))
        source = target or 'the file'
        return (
            f"This {tool_name.replace('-', ' ')} result is malicious for {source}. "
            f"VirusTotal flagged it with {detections}/{total} detections, so this is a strong warning sign rather than a clean result. "
            "From an OSINT perspective, the next step is to correlate the hash with sample names, distribution sources, family names, and related threat reports."
        )

    @staticmethod
    def _polish_analysis(tool_name: str, target: str, result_data: Dict, text: str) -> str:
        base = ResultInterpretationService._normalize_text(text)
        lead = ResultInterpretationService._lead_sentence(tool_name, target, result_data)
        why = ResultInterpretationService._why_sentence(tool_name, result_data)
        osint = ResultInterpretationService._osint_sentence(tool_name, result_data)
        return ' '.join(part for part in [lead, base, why, osint] if part).strip()

    @staticmethod
    def _normalize_text(text: str) -> str:
        cleaned = ' '.join(str(text or '').replace('\n', ' ').split())
        if not cleaned:
            return "No clear interpretation could be generated."
        if not cleaned.endswith('.'):
            cleaned += '.'
        return cleaned

    @staticmethod
    def _lead_sentence(tool_name: str, target: str, result_data: Dict) -> str:
        tool = (tool_name or '').lower()
        if tool in {'hash-checker', 'file-upload'}:
            vt = result_data.get('virustotal', {})
            if vt.get('is_malicious') or vt.get('detections', 0) > 0 or result_data.get('is_malicious') or result_data.get('detections', 0) > 0:
                return f"This {tool_name.replace('-', ' ')} result shows that {target or 'the file'} was flagged as suspicious or malicious."
            return f"This {tool_name.replace('-', ' ')} result does not show obvious malicious activity for {target or 'the file'}."
        if tool in {'ip-checker', 'check-ip'}:
            abuse_score = result_data.get('abuseipdb', {}).get('abuse_score', 0)
            detections = result_data.get('virustotal', {}).get('detections', 0)
            if abuse_score > 50 or detections > 0:
                return f"This IP reputation check shows warning signs for {target or 'the IP address'}."
            return f"This IP reputation check does not show strong warning signs for {target or 'the IP address'}."
        if tool in {'email-breach', 'email-osint'}:
            if result_data.get('breached'):
                return "This email investigation suggests the address may have been exposed in a breach."
            return "This email investigation does not show clear breach evidence right now."
        return f"This {tool_name.replace('-', ' ')} result gives us a snapshot of {target or 'the target'}."

    @staticmethod
    def _why_sentence(tool_name: str, result_data: Dict) -> str:
        tool = (tool_name or '').lower()
        if tool in {'hash-checker', 'file-upload'}:
            return "That matters because malware flags can indicate a dangerous sample, a false positive, or a file worth deeper review."
        if tool in {'ip-checker', 'check-ip'}:
            return "That matters because a risky IP can point to hosting infrastructure, abuse history, or a known malicious network."
        if tool in {'dns-lookup', 'subdomain-enum', 'whois-lookup', 'ssl-info'}:
            return "That matters because domain records, subdomains, and certificate details often expose ownership, infrastructure, and operational patterns."
        if tool in {'email-breach', 'email-osint'}:
            return "That matters because breached or exposed email data can reveal account risk, identity linkage, and further pivot points."
        if tool in {'geolocation', 'ip-geolocation', 'geo-lookup'}:
            return "That matters because location clues help narrow infrastructure, hosting region, or attribution leads."
        return "That matters because each OSINT result helps build a bigger picture around the target."

    @staticmethod
    def _osint_sentence(tool_name: str, result_data: Dict) -> str:
        tool = (tool_name or '').lower()
        if tool in {'hash-checker', 'file-upload'}:
            vt = result_data.get('virustotal', {})
            detections = vt.get('detections', 0) if isinstance(vt, dict) else 0
            total = vt.get('total_scanners', 0) if isinstance(vt, dict) else 0
            if vt.get('is_malicious') or detections > 0 or result_data.get('is_malicious') or result_data.get('detections', 0) > 0:
                return f"From an OSINT perspective, the detection ratio of {detections}/{total} should be treated as an indicator, then cross-checked with file reputation, sample context, and other malware intelligence."
            return "From an OSINT perspective, the clean result should still be cross-checked with filename, hash reuse, source, and surrounding context."
        if tool in {'ip-checker', 'check-ip'}:
            return "From an OSINT perspective, IP reputation should be combined with hosting history, ASN data, DNS, and related infrastructure before drawing conclusions."
        if tool in {'dns-lookup', 'subdomain-enum', 'whois-lookup', 'ssl-info'}:
            return "From an OSINT perspective, these details help map the target's infrastructure, timeline, and possible relationships to other assets."
        if tool in {'email-breach', 'email-osint'}:
            return "From an OSINT perspective, the email can be used as a pivot point to assess account reuse, exposure, and linked identities."
        if tool in {'geolocation', 'ip-geolocation', 'geo-lookup'}:
            return "From an OSINT perspective, location should be treated as a clue rather than exact proof, since it often reflects routing or hosting rather than the real operator."
        return "From an OSINT perspective, this result should be combined with other data points before forming a conclusion."

    @staticmethod
    def _fallback_interpretation(tool_name: str, target: str, result_data: Dict) -> str:
        tool = (tool_name or '').lower()
        if tool in {'hash-checker', 'file-upload'}:
            if ResultInterpretationService._is_confirmed_malicious(tool_name, result_data):
                return ResultInterpretationService._malicious_file_interpretation(tool_name, target, result_data)
            return (
                f"This file/hash does not appear to be flagged as malicious right now. "
                "That matters because a clean result reduces immediate concern, but it can still miss new or unknown samples. "
                "From an OSINT perspective, you should still verify the file source, filename pattern, and any surrounding intelligence."
            )
        if tool in {'ip-checker', 'check-ip'}:
            abuse_score = result_data.get('abuseipdb', {}).get('abuse_score', 0)
            detections = result_data.get('virustotal', {}).get('detections', 0)
            if abuse_score > 50 or detections > 0:
                return (
                    f"This IP reputation result shows warning signs for {target or 'the IP address'}. "
                    "That matters because higher abuse scores or detections can point to risky infrastructure or malicious use. "
                    "From an OSINT perspective, this should be cross-checked with ASN, DNS, and hosting context before making a final judgment."
                )
            return (
                f"This IP reputation result does not show strong warning signs for {target or 'the IP address'}. "
                "That matters because a cleaner reputation lowers immediate concern, but it does not prove the IP is harmless. "
                "From an OSINT perspective, the IP should still be compared with related domains and other infrastructure clues."
            )
        if tool in {'email-breach', 'email-osint'}:
            if result_data.get('breached'):
                return (
                    "This email shows signs of exposure and may have been part of a breach. "
                    "That matters because exposed emails can lead to credential reuse, account takeover, or identity linkage. "
                    "From an OSINT perspective, the address becomes a useful pivot for checking related usernames, domains, and breach history."
                )
            return (
                "This email does not currently show obvious breach indicators. "
                "That matters because the immediate exposure risk appears lower. "
                "From an OSINT perspective, the address can still be used as a pivot point for related intelligence if needed."
            )
        if tool in {'whois-lookup', 'dns-lookup', 'subdomain-enum', 'ssl-info'}:
            return (
                f"The domain data helps reveal how {target or 'the target'} is set up online. "
                "That matters because registration, DNS, and certificate details can expose infrastructure and ownership clues. "
                "From an OSINT perspective, these records are useful for mapping assets and identifying related services."
            )
        if tool in {'geolocation', 'ip-geolocation', 'geo-lookup'}:
            return (
                f"The location data gives a rough view of where {target or 'the IP address'} is registered or routed. "
                "That matters because it can narrow infrastructure context, even if it is not exact proof of physical location. "
                "From an OSINT perspective, location should be treated as a clue rather than a final conclusion."
            )
        return (
            f"Results for {target or 'this target'} were collected successfully and are ready for review. "
            "That matters because the target now has a usable intelligence snapshot. "
            "From an OSINT perspective, this result should be combined with other sources before drawing conclusions."
        )
