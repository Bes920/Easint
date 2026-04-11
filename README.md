# EASINT

EASINT is a Flask-based OSINT platform for collecting, saving, and analyzing investigation results in one place.

It combines:
- a tools workspace for OSINT lookups
- Supabase-backed investigation storage
- an investigation dashboard
- Gemini-powered AI chat
- one-click AI investigation analysis
- an OPSEC learning page

Current version: `v0.0.1`

## Overview

EASINT is designed around a simple workflow:

1. Run a tool from `/tools`
2. Save the result into an investigation automatically
3. Review results in `/dashboard`
4. Ask the AI questions or generate a full AI summary

## Main Pages

| Route | Description |
| --- | --- |
| `/` | Landing page |
| `/tools` | Main OSINT tools workspace |
| `/dashboard` | Investigation dashboard with AI features |
| `/opsec` | OPSEC / learning page |
| `/ai-test` | Standalone AI test page |

## Current Features

### OSINT Tools
- file upload and hash analysis
- EXIF metadata extraction
- IP reputation checking
- IP geolocation
- reverse IP lookup
- MAC lookup
- Shodan search
- WHOIS lookup
- DNS lookup
- subdomain enumeration
- SSL certificate lookup
- Wayback Machine search
- email OSINT
- email breach checks
- username search
- phone lookup
- Google dork generation
- crypto tracking

### Investigation Dashboard
- create investigations
- update status
- delete investigations
- review saved results
- see threat badges
- inspect result timelines

### AI Features
- ask questions about an investigation with `POST /ai/chat`
- generate one-click investigation summaries with `POST /ai/analyze/<investigation_id>`
- view threat level, summary, insights, correlations, and recommended actions
- use inline dashboard chat with animated loading states

## Quick Start

### Requirements
- Python 3.10+ recommended
- Supabase project
- internet access for external APIs
- optional: ExifTool
- optional: Gemini API key

### Install

```bash
git clone <your-repo-url>
cd osint-fixed

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
pip install google-genai
```

### Environment Variables

Create a `.env` file in the project root.

Required to start the app:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

Optional keys used by current features:

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

### Optional ExifTool

```bash
# Ubuntu / Debian
sudo apt-get install exiftool

# macOS
brew install exiftool
```

### Run

```bash
source venv/bin/activate
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## API Summary

### Tool Routes

| Category | Routes |
| --- | --- |
| File analysis | `/upload-file`, `/check-hash`, `/extract-exif` |
| Network | `/check-ip`, `/geolocate-ip`, `/reverse-ip`, `/mac-lookup`, `/shodan-search` |
| Domain | `/whois-lookup`, `/dns-lookup`, `/subdomain-enum`, `/ssl-info`, `/wayback-machine` |
| Identity | `/email-osint`, `/email-breach`, `/username-search`, `/phone-lookup` |
| Research | `/google-dork`, `/crypto-tracker` |
| Export | `/export-results` |

### Investigation Routes

| Route | Method | Purpose |
| --- | --- | --- |
| `/api/investigations` | `GET` | List investigations |
| `/api/investigations` | `POST` | Create investigation |
| `/api/investigations/<investigation_id>` | `GET` | Get one investigation with details |
| `/api/investigations/<investigation_id>` | `PUT` | Update status |
| `/api/investigations/<investigation_id>` | `DELETE` | Delete investigation |
| `/api/investigations/<investigation_id>/results` | `GET` | Get investigation results |

### AI Routes

| Route | Method | Purpose |
| --- | --- | --- |
| `/ai/chat` | `POST` | Ask questions about an investigation |
| `/ai/analyze/<investigation_id>` | `POST` | Generate full AI summary |
| `/ai/test` | `GET` | Check AI route registration / Gemini status |

## How Storage Works

The app saves tool results through Supabase using:
- `investigations`
- `investigation_results`
- `chat_history`

If a tool result is created without a selected investigation, the app stores it in:

```text
Auto-saved Results
```

Important: Supabase is required at startup. If `SUPABASE_URL` or `SUPABASE_KEY` is missing, the app will fail during import.

## Project Structure

### Core Backend
- [app.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/app.py)
- [routes/ai_routes.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/routes/ai_routes.py)
- [services/results_service.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/services/results_service.py)
- [services/investigation_service.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/services/investigation_service.py)
- [services/gemini_ai_service.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/services/gemini_ai_service.py)
- [services/chat_service.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/services/chat_service.py)
- [config/supabase_config.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/config/supabase_config.py)

### Frontend
- [templates/home.html](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/templates/home.html)
- [templates/index.html](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/templates/index.html)
- [templates/dashboard.html](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/templates/dashboard.html)
- [templates/opsec.html](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/templates/opsec.html)
- [templates/ai_test.html](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/templates/ai_test.html)
- [static/js/script.js](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/static/js/script.js)
- [static/js/dashboard.js](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/static/js/dashboard.js)
- [static/js/ai_chat.js](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/static/js/ai_chat.js)
- [static/css/dashboard.css](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/static/css/dashboard.css)

## Diagnostics

Helper scripts included in the repo:
- [test_gemini_api.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/test_gemini_api.py)
- [test_mistral.py](/home/exploitforge/Documents/School/finalyear/proto/osint-fixed/test_mistral.py)

Examples:

```bash
python test_gemini_api.py
python test_mistral.py
```

## Known Limitations

- PDF export in the dashboard is still a placeholder
- some tools depend on third-party APIs and may fail without keys
- chat persistence helpers exist, but the dashboard currently sends empty chat history to the AI route

## Troubleshooting

### App fails with Supabase configuration error

Check your `.env`:

```env
SUPABASE_URL=...
SUPABASE_KEY=...
```

### AI features fail

Check:
- `GEMINI_API_KEY` is set
- `google-genai` is installed
- the app was restarted after updating `.env`

### Results are not being saved

Check:
- Supabase credentials are valid
- required tables exist
- your key has the required permissions

### EXIF extraction fails

Install ExifTool and ensure it is available in your system path.

## Summary

EASINT currently provides:
- multi-tool OSINT collection
- automatic result saving
- investigation management
- dashboard review workflows
- AI chat
- full AI investigation summaries
