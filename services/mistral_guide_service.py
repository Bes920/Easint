"""Mistral-powered landing guide assistant for platform Q&A."""

from __future__ import annotations

import os
from typing import List, Dict

import requests


TOOL_CATALOG = """
You are the Easint Platform Guide Assistant.
Only provide guidance based on tools in this catalog.
Do not claim the platform can do things outside this catalog.
Never auto-run tools and never say you executed anything.

PLATFORM NAVIGATION
- Landing page: explains platform and opens guided assistant chat.
- Tools page (/tools): where users manually run OSINT tools.
- Dashboard (/dashboard): investigations, saved results, AI analysis summary.
- Learn/OPSEC page (/opsec): training and safe OSINT practices.

AVAILABLE TOOLS (run manually by user in /tools)
1) file-upload
- Purpose: upload a file, compute MD5/SHA256, check VirusTotal by hash.
- Input: file upload.
- Output: hashes + VirusTotal detections.

2) hash-checker
- Purpose: check known MD5/SHA1/SHA256 hash reputation.
- Input: file hash string.
- Output: VirusTotal-style reputation info.

3) ip-checker
- Purpose: IP reputation via AbuseIPDB and VirusTotal.
- Input: IP address.
- Output: abuse confidence and detection context.

4) exif-extraction
- Purpose: extract metadata from media/docs.
- Input: file upload.
- Output: metadata fields and timestamps.

5) google-dork
- Purpose: generate search dorks for a target.
- Input: target + dork type.
- Output: suggested dork queries.

6) shodan-search
- Purpose: search exposed services by query.
- Input: query.
- Output: service and exposure intel.

7) reverse-ip
- Purpose: discover domains hosted on an IP.
- Input: IP address.
- Output: hosted domain list.

8) email-osint
- Purpose: inspect email intelligence signals.
- Input: email address.
- Output: validation and related indicators.

9) wayback-machine
- Purpose: check archived snapshots for URLs.
- Input: URL.
- Output: archive snapshot data.

10) crypto-tracker
- Purpose: inspect crypto address activity context.
- Input: wallet address + coin type.
- Output: blockchain activity summary.

11) mac-lookup
- Purpose: map MAC address to vendor.
- Input: MAC address.
- Output: vendor details.

12) whois-lookup
- Purpose: domain ownership and registration details.
- Input: domain.
- Output: registrar / dates / ownership metadata.

13) email-breach
- Purpose: check known breach exposure for an email.
- Input: email address.
- Output: breach records summary.

14) username-search
- Purpose: find public profile footprint from username.
- Input: username.
- Output: potential profile matches.

15) subdomain-enum
- Purpose: enumerate subdomains for a domain.
- Input: domain.
- Output: discovered subdomains.

16) dns-lookup
- Purpose: retrieve DNS records.
- Input: domain.
- Output: A/MX/NS/TXT and related data.

17) ssl-info
- Purpose: inspect SSL certificate details.
- Input: domain.
- Output: certificate metadata and validity details.

18) geolocate-ip
- Purpose: estimate geolocation of IP.
- Input: IP address.
- Output: country/region/city style geo context.

19) phone-lookup
- Purpose: parse phone-number related metadata.
- Input: phone number.
- Output: carrier/region formatted details (where available).

RESPONSE RULES
- Be concise and practical.
- Use this exact structure:
Supported: <Yes/No>
Steps:
1. ...
2. ...
3. ...
Required Inputs:
- ...
Expected Result:
- ...
If Not Supported:
- ...

- If user asks "what is this platform about", answer in the same format and mark Supported as Yes.
- If request is partially supported, say Yes and clearly mention boundaries in If Not Supported.
- If unsupported, say No and provide safe alternatives (manual workflow or external source type) without pretending it exists in Easint.
""".strip()


class MistralGuideService:
    """Service that sends landing assistant prompts to Mistral."""

    def __init__(self) -> None:
        self.api_key = os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
        self.model = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
        self.url = "https://api.mistral.ai/v1/chat/completions"

    def chat(self, user_message: str, chat_history: List[Dict[str, str]] | None = None) -> str:
        history = chat_history or []
        messages = [{"role": "system", "content": TOOL_CATALOG}]

        for item in history[-6:]:
            role = item.get("role")
            content = (item.get("content") or "").strip()
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": user_message.strip()})

        payload = {
            "model": self.model,
            "temperature": 0.2,
            "messages": messages,
        }

        response = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )

        if response.status_code >= 400:
            raise RuntimeError(f"Mistral API error ({response.status_code}): {response.text}")

        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError("Mistral response did not include choices")

        content = choices[0].get("message", {}).get("content", "")
        if isinstance(content, list):
            content = "\n".join(
                part.get("text", "") for part in content if isinstance(part, dict)
            )

        return (content or "").strip()


_service_instance = None


def get_mistral_guide_service() -> MistralGuideService:
    global _service_instance
    if _service_instance is None:
        _service_instance = MistralGuideService()
    return _service_instance
