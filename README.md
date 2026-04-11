# EASINT

Professional OSINT platform built with Flask, Supabase, and Gemini-powered investigation assistance.

The app currently ships with:
- a guided home page
- a tools workspace for OSINT lookups
- a dashboard for saved investigations
- AI chat inside investigation details
- one-click AI investigation analysis with threat badges and structured summaries
- an OPSEC learning page

Current version: `v0.0.1`

## What The App Does

EASINT lets you run OSINT checks, automatically save results into investigations, and then review or analyze those results later from the dashboard.

Main workflows:
1. Open `/tools` and run an OSINT tool.
2. The result is auto-saved to a selected investigation, or to `Auto-saved Results`.
3. Open `/dashboard` to review investigations and results.
4. Ask the AI questions about an investigation, or click `Analyze Investigation` for a full summary.

## Current Pages

| Route | Purpose |
| --- | --- |
| `/` | Home / landing page |
| `/tools` | Main OSINT tool workspace |
| `/dashboard` | Investigation management and AI-assisted review |
| `/opsec` | OPSEC / OSINT learning page |
| `/ai-test` | Standalone AI test page |

## Current AI Features

AI functionality is provided through the blueprint in [routes/ai_routes.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/routes/ai_routes.py).

Available AI endpoints:
- `POST /ai/chat`
- `POST /ai/analyze/<investigation_id>`
- `GET /ai/test`

What is already implemented in the dashboard:
- inline AI chat per investigation
- suggested quick questions
- animated loading state while the AI is thinking
- one-click investigation analysis
- executive summary
- key insights
- correlations
- recommended actions
- overall threat badge with visual severity state

## Current Tool Endpoints

These routes are defined in [app.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/app.py).

| Category | Endpoints |
| --- | --- |
| File analysis | `/upload-file`, `/check-hash`, `/extract-exif` |
| Network / infra | `/check-ip`, `/geolocate-ip`, `/reverse-ip`, `/mac-lookup`, `/shodan-search` |
| Domain / DNS | `/whois-lookup`, `/dns-lookup`, `/subdomain-enum`, `/ssl-info`, `/wayback-machine` |
| Identity / people | `/email-osint`, `/email-breach`, `/username-search`, `/phone-lookup` |
| Research / advanced | `/google-dork`, `/crypto-tracker` |
| Export | `/export-results` |
| Investigations API | `/api/investigations`, `/api/investigations/<investigation_id>`, `/api/investigations/<investigation_id>/results` |

## Architecture

### Backend
- [app.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/app.py): Flask app, main routes, API integrations, investigation APIs
- [routes/ai_routes.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/routes/ai_routes.py): AI chat and investigation analysis routes
- [services/results_service.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/services/results_service.py): auto-save logic and threat heuristics
- [services/investigation_service.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/services/investigation_service.py): investigation CRUD and result retrieval
- [services/gemini_ai_service.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/services/gemini_ai_service.py): Gemini prompts and response parsing
- [services/chat_service.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/services/chat_service.py): chat history helpers for Supabase
- [config/supabase_config.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/config/supabase_config.py): Supabase client initialization

### Frontend
- [templates/home.html](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/templates/home.html): landing page
- [templates/index.html](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/templates/index.html): tools page
- [templates/dashboard.html](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/templates/dashboard.html): investigations UI and AI modal
- [templates/opsec.html](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/templates/opsec.html): OPSEC page
- [templates/ai_test.html](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/templates/ai_test.html): standalone AI playground
- [static/js/script.js](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/static/js/script.js): main tools page behavior
- [static/js/dashboard.js](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/static/js/dashboard.js): dashboard state, AI chat, AI analysis UI
- [static/js/ai_chat.js](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/static/js/ai_chat.js): standalone AI test page logic
- [static/js/theme.js](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/static/js/theme.js): theme coordination

## Data Flow

1. A tool request is submitted from the tools UI.
2. The backend returns structured JSON.
3. [services/results_service.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/services/results_service.py) saves the result to Supabase.
4. If no investigation is selected, the app uses `Auto-saved Results`.
5. The dashboard loads investigations through `/api/investigations`.
6. Opening an investigation modal loads results and enables AI chat plus full AI analysis.

## Setup

### Requirements
- Python 3.10+ recommended
- Supabase project and credentials
- Internet access for external API-backed tools
- Optional: ExifTool for richer metadata extraction
- Optional: Gemini API key for AI features

### Install

```bash
git clone <your-repo-url>
cd osint-fixed

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root.

Required for the app to start:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_or_anon_key
```

Optional but used by features already in the code:

```env
VIRUSTOTAL_API_KEY=your_key
ABUSEIPDB_API_KEY=your_key
HIBP_API_KEY=your_key
SHODAN_API_KEY=your_key
HUNTER_API_KEY=your_key
BLOCKCHAIN_API_KEY=your_key
GEMINI_API_KEY=your_key
MISTRAL_API_KEY=your_key
```

### Gemini Dependency

The current code imports `google.genai` in [services/gemini_ai_service.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/services/gemini_ai_service.py), so if it is not already available in your environment install it before using AI features:

```bash
pip install google-genai
```

### Optional ExifTool

```bash
# Ubuntu / Debian
sudo apt-get install exiftool

# macOS
brew install exiftool
```

## Run The App

```bash
source venv/bin/activate
python app.py
```

Default URL:

```text
http://127.0.0.1:5000
```

## Investigation Dashboard

The dashboard is not just a list view anymore. It currently supports:
- investigation creation
- status updates
- deletion
- tag display
- result timelines
- threat badge rendering
- AI chat inside the details modal
- one-click `Analyze Investigation` summaries

Important frontend files:
- [templates/dashboard.html](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/templates/dashboard.html)
- [static/js/dashboard.js](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/static/js/dashboard.js)
- [static/css/dashboard.css](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/static/css/dashboard.css)

## AI Investigation Analysis

When a saved investigation has results, the dashboard can send the full investigation to:

```text
POST /ai/analyze/<investigation_id>
```

The response is rendered into:
- overall threat
- executive summary
- key insights
- correlations
- recommended actions

The dashboard also supports:

```text
POST /ai/chat
```

for question-and-answer style interaction about the same investigation.

## Testing / Diagnostics

Available helper scripts:
- [test_gemini_api.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/test_gemini_api.py): checks Gemini connectivity
- [test_mistral.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/test_mistral.py): checks Mistral connectivity

Useful checks:

```bash
python test_gemini_api.py
python test_mistral.py
```

You can also verify the AI blueprint directly:

```text
GET /ai/test
```

## Notes About Storage

The current code expects Supabase tables for:
- `investigations`
- `investigation_results`
- `chat_history`

The app relies on Supabase during import, so missing `SUPABASE_URL` or `SUPABASE_KEY` will prevent startup.

## Known Gaps / Current State

This README reflects the code as it exists now, including a few practical realities:
- PDF export in the dashboard is still a placeholder
- some helper/test files exist for experimentation
- some external tools depend on third-party APIs and may fall back or fail when keys are missing
- AI chat history persistence helpers exist, but the dashboard currently sends an empty chat history on each request

## Troubleshooting

### App fails on startup with Supabase error

Check that your `.env` includes:

```env
SUPABASE_URL=...
SUPABASE_KEY=...
```

### AI routes return configuration errors

Check:
- `GEMINI_API_KEY` is set
- `google-genai` is installed
- the server was restarted after updating `.env`

### Tool results are not being saved

Check:
- Supabase credentials are valid
- required tables exist
- the API key used by Supabase has insert/select permission

### Exif extraction fails

Install ExifTool and ensure it is available on your system path.

## Summary

EASINT in its current codebase is a Flask OSINT platform with:
- multi-tool OSINT workflows
- Supabase-backed investigation storage
- automatic result saving
- dashboard-based investigation review
- Gemini-powered AI chat
- Gemini-powered one-click investigation analysis
