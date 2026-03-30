# 🔍 **EASINT** - Professional OSINT Intelligence Platform

> **18+ Investigation Tools | Production-Ready | For Security Researchers & Analysts**

A **professional-grade Open Source Intelligence (OSINT) platform** that replaces expensive, complex investigation workflows. Instead of juggling 5-10 different websites and tools, EASINT brings its investigation, analysis, and learning workflows into one unified interface. The production app opens on a guided homepage, then routes users into the tool workspace, the investigation dashboard, or the OPSEC learning area.

---

## ✨ **Key Features**

| Feature | Description |
|---------|-------------|
| 📤 **File Upload & Scanning** | Upload files (up to 32MB) → Auto MD5/SHA256 → VirusTotal malware check |
| 📸 **Metadata Extraction** | Extract EXIF from images, PDFs, documents (GPS, camera info, etc.) |
| 🔎 **Google Dorking** | Auto-generate advanced Google search queries in 4 categories |
| 🌐 **IP Intelligence** | Check IP reputation via AbuseIPDB + VirusTotal (dual verification) |
| 🗺️ **Geolocation** | Pinpoint IP location, ISP, country information |
| 🔄 **Reverse IP** | Find all domains hosted on a specific IP address |
| 📧 **Email OSINT** | Validate emails, check MX records, breaches |
| 🏢 **Domain Info** | WHOIS lookup, DNS records, SSL certificates |
| 🔍 **Subdomain Finder** | Enumerate subdomains of target domain |
| 📸 **Wayback Machine** | Check historical website snapshots |
| 👤 **Username Search** | Find social media accounts across 10+ platforms |
| 🖥️ **Mac Lookup** | Identify device vendors by MAC address |
| 💾 **Export Results** | Download findings as JSON for reports |
| 🧹 **Clean Interface** | Professional dark theme, easy navigation |
| 🤖 **AI Analyst Chat** | Select a saved investigation and open the detail modal to ask Gemini-powered questions, view typing indicators, and see responses inside the investigation UI. |
| 🏠 **Guided Homepage** | Production-ready landing page that introduces the platform and routes users to the right workspace |
| 🧭 **Cross-Page Navigation** | Direct navigation between Home, Tools, Dashboard, and Learn OSINT pages |

---


- Guided homepage for first-time and returning users.
- Clear movement between workspaces without losing orientation.
- Professional investigation workflow with saved results and AI analysis.

---

## 🎯 **Complete Tool List (18 Tools)**

### **File Analysis (3 tools)**
1. ✅ **File Upload & Hash** - Upload → MD5/SHA256 → VirusTotal
2. ✅ **Hash Lookup** - Manual hash checking
3. ✅ **ExifTool** - Metadata extraction

### **Network & Security (5 tools)**
4. ✅ **IP Reputation** - AbuseIPDB + VirusTotal dual check
5. ✅ **IP Geolocation** - Location tracking
6. ✅ **Reverse IP** - Find domains on IP
7. ✅ **MAC Lookup** - Device vendor identification
8. ✅ **Shodan Search** - IoT/device discovery (template)

### **Domain & DNS (5 tools)**
9. ✅ **WHOIS** - Domain registration info
10. ✅ **DNS Records** - Complete DNS analysis
11. ✅ **Subdomain Finder** - Discover subdomains
12. ✅ **SSL Certificate** - TLS/SSL validation
13. ✅ **Wayback Machine** - Historical snapshots

### **People & Accounts (3 tools)**
14. ✅ **Email OSINT** - Email validation & MX records
15. ✅ **Breach Check** - Have I Been Pwned
16. ✅ **Username Search** - 10+ social platforms

### **Advanced (2 tools)**
17. ✅ **Google Dorking** - Advanced search queries
18. ✅ **Crypto Tracker** - Cryptocurrency wallets

### **AI Assistant**
19. ✅ **Investigation Chat & Analysis** - Converse with Gemini about investigation results, ask for correlations, and receive summarized threat assessments.

---

## 🚀 **Quick Start (5 Minutes)**

### **📋 Prerequisites**
- Python 3.8+
- Git
- pip (Python package manager)
- Optional: ExifTool for metadata extraction

### **⬇️ Step 1: Clone & Setup**

```bash
# Clone the repository
git clone git@github.com:Bes920/Easint.git
cd Easint

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **🔑 Step 2: Configure API Keys**

1. **Create a `.env` file in the project root:**
```bash
touch .env
```

2. **Edit `.env` and add your API keys:**
```env
VIRUSTOTAL_API_KEY=your_key_here
ABUSEIPDB_API_KEY=your_key_here
HIBP_API_KEY=your_key_here
SHODAN_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

**Get Free API Keys:**
- 🔴 **VirusTotal** → https://www.virustotal.com/gui/join-us (free tier)
- 🟡 **AbuseIPDB** → https://www.abuseipdb.com/register (free tier)
- 🔵 **HIBP** → https://haveibeenpwned.com/API/Key (free tier)
- 🟠 **Shodan** → https://account.shodan.io/ (optional)

### **📸 Step 3: (Optional) Install ExifTool**

For full metadata extraction from files:

```bash
# macOS
brew install exiftool

# Linux (Debian/Ubuntu)
sudo apt-get install exiftool

# Linux (Fedora)
sudo dnf install perl-Image-ExifTool

# Windows
# Download from: https://exiftool.org/
```

### **▶️ Step 4: (Optional) Enable AI Assistant**

- Install the Gemini client:

```bash
pip install google-genai --break-system-packages
```

- Make sure `GEMINI_API_KEY` is set in `.env`
- Run `python test_gemini_api.py` to list available models and confirm the key is valid before opening the chat features
- Once the server is running, open `/dashboard`, click an investigation, and interact with the new AI Analysis section at the bottom of the modal (typed messages or quick-question buttons trigger `/ai/chat` and show replies inline).

### **▶️ Step 5: Run the Application**

```bash
# Make sure your virtual environment is activated
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Start the application
python app.py
```

**Output:**
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### **🌐 Step 6: Open in Browser**

Visit: **http://localhost:5000** 🎉

### **🗺️ Route Overview**

- `/` opens the guided homepage
- `/tools` opens the full OSINT tool workspace
- `/dashboard` opens saved investigations and AI-assisted analysis
- `/opsec` opens the OPSEC and OSINT learning area
- Dashboard and OPSEC both include direct links back to the homepage

---

## 🧱 **Architecture Overview**

### How the pieces fit together
- **Flask backend (`app.py`)** exposes REST endpoints for each OSINT tool, handles uploads, formats API responses, and coordinates investigation metadata by calling `services/results_service.py` and `services/investigation_service.py`.
- **Frontend assets (`static/js/` + templates)** breathe life into the user experience: `script.js` drives the main tool dashboard, `dashboard.js` owns the investigation management UI, and `opsec.js` powers the OPSEC education page while `theme.js` keeps them all in sync on look-and-feel.
- **Supabase (`config/supabase_config.py`) stores state** in tables such as `investigations`, `investigation_results`, and `chat_history` so every tool result can be auto-saved and reviewed later.
- **External APIs** (VirusTotal, AbuseIPDB, HIBP, MAC Vendors, DNS, WHOIS, etc.) are queried by helper functions in `app.py`, and fall back to safe demo messages when keys are missing.

### Key data flows
1. **Tool request**: user submits a form → browser sends a POST to `/check-ip`, `/google-dork`, `/hash-check`, etc. → backend enriches the payload with API responses → `ResultsService` automatically saves the output to the currently selected investigation (defaulting to the “Auto-saved Results” investigation if none is selected).
2. **Workspace routing**: `/` introduces the platform, while the primary navigation moves users into `/tools`, `/dashboard`, or `/opsec` depending on whether they want to investigate, manage saved work, or learn.
3. **Investigation dashboard**: `/api/investigations` populates the sidebar dropdown on the tools page, while `/dashboard` renders the management interface powered by `dashboard.js`.
4. **Investigation lifecycle**: results are grouped per investigation via `InvestigationService.add_investigation_result` with threat-level heuristics, and CRUD operations + status updates/deletions are handled via dedicated REST endpoints.

## 🤖 **AI Assistant & Investigation Insights**

- **Blueprint & routes**: `routes/ai_routes.py` registers a dedicated `/ai` blueprint that exposes `/chat` for conversational questions, `/analyze/<investigation_id>` for AI-generated executive summaries, and `/test` to verify the Gemini connection. `app.py` mounts the blueprint and adds a `/ai-test` view so the chat UI can be exercised independently alongside the dashboard.
- **Gemini service**: `services/gemini_ai_service.py` wraps `google-genai`/Gemini, builds structured prompts from `InvestigationService.get_investigation_with_results`, and exposes `chat`, `analyze_result`, and `analyze_investigation` helpers to assess threat levels, extract findings, correlations, and recommend next steps.
- **Dashboard integration**: `templates/dashboard.html` now includes the AI Analysis section in the investigation details modal, while `static/js/dashboard.js` handles the chat state (`initializeDashboardChat`, typing indicator, quick-answer buttons, and `/ai/chat` requests). The newest CSS block in `static/css/dashboard.css` styles the chat bubbles, typing indicator, and related controls.
- **Legacy UI**: The standalone `templates/ai_test.html` + `static/js/ai_chat.js` remain available for direct experimentation, showing typing indicators and quick-question shortcuts; their responses now mirror what the dashboard provides inside each investigation.
- **Chat persistence (future-ready)**: `services/chat_service.py` centralizes Supabase interactions for saving sessions and histories so conversational context can later be reloaded or audited.
- **Test harness**: `test_gemini_api.py` lists available Gemini models and generates a “hello” prompt so you know the key, network, and `google-genai` install are working before relying on the assistant in production.

## 🧭 **Investigations & Auto-save Flow**

- The dropdown on the tools page (and mirrored in `theme.js`) loads every investigation via `/api/investigations`, prioritizes the auto-save one, and persists the user's choice in `localStorage`.
- When a tool posts data, `static/js/script.js` injects `investigation_id` automatically so the backend knows where to stash the result. `ResultsService.save_tool_result` creates the default investigation if needed, while `determine_threat_level` provides quick categorization (e.g., VirusTotal detection = `critical`).
- The investigation dashboard at `/dashboard` lets analysts filter/search investigations, inspect results, change statuses, or delete entire investigations. Every change reflates back to Supabase via the service layer with consistent timestamps/metadata.
- From both `/dashboard` and `/opsec`, users can now jump directly back to the homepage to switch context without retracing through the tools page first.

## 🛠️ **Tool-to-Endpoint Snapshot**

| Category | Frontend form (`templates` + `static/js/script.js`) | Backend route (`app.py`) |
| --- | --- | --- |
| File analysis | File upload form, Hash checker, ExifTool | `/upload-file`, `/check-hash`, `/extract-exif` |
| Network | IP reputation, Geolocation, Reverse IP, MAC lookup | `/check-ip`, `/geolocate-ip`, `/reverse-ip`, `/mac-lookup` |
| Domain | WHOIS, DNS, Subdomains, SSL, Wayback | `/whois-lookup`, `/dns-lookup`, `/subdomain-enum`, `/ssl-info`, `/wayback-machine` |
| People | Email OSINT, Breach, Username search | `/email-osint`, `/email-breach`, `/username-search` |
| Advanced | Google Dork, Crypto tracker, Shodan, Phone lookup | `/google-dork`, `/crypto-tracker`, `/shodan-search`, `/phone-lookup` |

Each tool returns structured JSON that `script.js` renders into the UI with badges, lists, and helper links, keeping the experience consistent while the backend handles the heavy lifting.

## ⚙️ **Testing & Diagnostics**

- `test_mistral.py` validates the Mistral AI client connection (requires `MISTRAL_API_KEY`), ensuring the AI side of future features can talk to the API without surprises.
- `test_gemini_api.py` lists available Gemini models, pings the API, and generates a short response so you know `GEMINI_API_KEY` + `google-genai` are configured before opening `/ai-test`.
- These scripts print guided outputs/error handling, making it easy to see what needs fixing before launching the UI.

## 📖 **How It Works**

### **What is OSINT?**
Open Source Intelligence (OSINT) is gathering information from publicly available sources. This platform automates 18+ common investigation techniques:

### **Investigation Workflow:**
```
1. Input (Domain/IP/Email/File)
   ↓
2. Intelligence Gathering (Query APIs, DNS, etc.)
   ↓
3. Analysis (Check reputation, find links, extract data)
   ↓
4. Results (Display findings, export to JSON)
```

### **Example: Domain Investigation**
```
You search: example.com
↓
Platform performs:
  • WHOIS lookup (owner info)
  • DNS records (mail servers, nameservers)
  • SSL certificate analysis
  • Subdomain enumeration
  • Wayback Machine snapshots
  • Reverse IP lookup
↓
View all connections & export report
```

---

## ⚙️ **Troubleshooting**

### **Issue: "ModuleNotFoundError: No module named 'flask'"**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Then install dependencies
pip install -r requirements.txt
```

### **Issue: "API Key Error" or "Demo Mode"**
- ✅ Verify `.env` file exists in project root
- ✅ Check API key format is correct (no spaces)
- ✅ Restart the application after adding keys
- ✅ Verify the app is loading from `.env` (check terminal output)

### **Issue: ExifTool Not Found**
```bash
# Install ExifTool (optional but recommended)
# macOS:
brew install exiftool

# Linux:
sudo apt-get install exiftool

# Windows:
# Download: https://exiftool.org/
```

### **Issue: Port 5000 Already In Use**
```bash
# Change port in app.py or run on different port:
python -c "import app; app.app.run(port=5001)"
```

### **Issue: Database/File Upload Errors**
- ✅ Ensure `uploads/` folder exists
- ✅ Check folder permissions: `chmod 755 uploads/`
- ✅ Verify disk space available
- ✅ Check file size doesn't exceed 32MB limit

### **Issue: DNS/Network Errors**
- ✅ Check internet connectivity: `ping google.com`
- ✅ Verify API endpoints are accessible
- ✅ Check firewall/proxy settings
- ✅ Try again later (API temporary outage)

---

## 🚀 **Why This Web App Beats Traditional OSINT**

### **The Problem with Traditional OSINT**
Traditional OSINT investigations require:
- ❌ **Manual searching** - Google, WHOIS, DNS lookup tools, each handled separately
- ❌ **Context switching** - Moving between 5-10 different websites and command lines
- ❌ **Copy-pasting** - Hash values, file names, IP addresses between different platforms
- ❌ **No workflows** - Scattered results, hard to track investigation progress
- ❌ **Time consuming** - Each query takes minutes, manual data correlation
- ❌ **Error-prone** - Typing mistakes, URLs get mistyped, data gets lost
- ❌ **Expensive tools** - Professional OSINT platforms cost $500-5000/month

### **The EASINT Solution**
EASINT centralizes ALL investigation tools in one interface:

✅ **All-in-One Dashboard** - 18 tools accessible from one clean interface  
✅ **One-Click Intelligence** - Enter IP/Domain/Email → Get instant results from multiple sources  
✅ **Dual Verification** - IP reputation checked through BOTH AbuseIPDB AND VirusTotal simultaneously  
✅ **Smart Workflows** - Results auto-clear when switching investigations, no confusion  
✅ **Instant Correlation** - See how entities link (IP → domains, email → accounts, file → reputation)  
✅ **Professional Exports** - Download investigation results as JSON for reports  
✅ **Zero License Cost** - 100% free, open-source alternative to paid platforms  

### **Real-World Time Savings**

| Task | Traditional | EASINT |
|------|-----------|--------|
| **IP Reputation Check** | Visit AbuseIPDB (2 min) + VirusTotal (2 min) + cross-check (1 min) = **5 min** | Click "Check IP" = **10 seconds** |
| **Domain Investigation** | WHOIS (2 min) + DNS lookup (1 min) + SSL check (2 min) + Wayback (1 min) = **6 min** | Single search = **20 seconds** |
| **Email Breach Check** | Visit HIBP + verify results + check social = **5 min** | One click = **5 seconds** |
| **File Analysis** | Upload to VirusTotal + wait for scan + check metadata = **3 min** | Upload + Auto hash + Auto scan = **1 min** |
| **Investigation Report** | Manually copy results + paste into document = **10 min** | Export to JSON = **5 seconds** |

**Result: 30-minute investigation takes 1 minute with EASINT** ⚡

---

## 🛡️ **Security Features**

✅ Input validation on all forms  
✅ File upload size limits (32MB)  
✅ Secure filename handling  
✅ Investigation persistence through Supabase-backed services  
✅ API key environment variable support  
✅ Rate limiting ready  
✅ CORS security headers  

---

## 📊 **Use Case Examples**

### **Malware Analysis Workflow:**
1. Upload suspicious file → Get hashes
2. VirusTotal scan → Check reputation
3. ExifTool → Extract metadata
4. Export results → Document findings

### **Domain Investigation:**
1. WHOIS → Get owner info
2. DNS → Find mail servers
3. Subdomain → Discover infrastructure
4. SSL → Verify certificates
5. Reverse IP → Find related domains
6. Wayback → Check history

### **Email Investigation:**
1. Email OSINT → Validate address
2. Breach Check → Find leaks
3. Username Search → Find accounts
4. Google Dork → Search mentions
5. Export → Create report

---

## 🎨 **UI/UX Excellence**

- **Guided homepage** - Clear entry points for first-time and repeat users
- **Professional dark theme** - OSINT aesthetic
- **Cross-page navigation** - Direct movement between Home, Tools, Dashboard, and Learn OSINT
- **Sidebar navigation** - Easy tool switching within each workspace
- **Result clearing** - Clean investigation flow
- **Loading indicators** - User feedback
- **Error handling** - Graceful failures
- **Responsive design** - Mobile-friendly
- **Export button** - One-click reporting

---

## 🔧 **Technical Implementation**

### **Backend (Python/Flask):**
- RESTful API architecture
- File upload handling (Werkzeug)
- Multi-threading capable
- Error handling & validation
- Modular function design

### **Frontend (HTML/CSS/JS):**
- Vanilla JavaScript (no framework bloat)
- Event-driven architecture
- Asynchronous API calls
- Dynamic result rendering
- Professional CSS animations

### **Integration:**
- VirusTotal API v3
- AbuseIPDB API v2
- HIBP API v3
- DNS queries (dnspython)
- WHOIS lookups (python-whois)
- ExifTool subprocess calls
- Wayback Machine API
- Free geolocation APIs

---

## 📝 **Extending the Platform**

### **Easy to Add:**
- New API integrations
- Additional tools
- Database storage
- User authentication
- Batch processing
- PDF report generation
- Real-time updates

### **Recommended Enhancements:**
- PostgreSQL for result storage
- Redis for caching
- Celery for background jobs
- Docker containerization
- API rate limit handling
- Advanced correlation engine

---

## ⚠️ **Important Notes**

### **ExifTool:**
- Not required but HIGHLY recommended
- Install separately (not pip package)
- Without it, basic file info only
- Installation commands in Quick Start

### **API Limits (Free Tiers):**
- VirusTotal: 4 req/min, 500/day
- AbuseIPDB: 1000 req/day
- HIBP: 10 req/min

### **Working Without APIs:**
- 10+ tools work immediately
- File upload works (no VT scan)
- ExifTool works independently
- Google Dorks work (no API needed)
- Most domain/network tools work

---

## 📚 **Learning Resources**

EASINT can be used to understand:
- **OSINT Fundamentals** - Hands-on experience with real investigation techniques
- **API Integration** - See how to connect to threat intelligence APIs securely
- **Web Development** - Clean Python backend with responsive frontend
- **Security Best Practices** - Input validation, API key management, file handling
- **Data Correlation** - Learn how individual data points connect in investigations

---

## 📞 **Support & Resources**

- **OSINT Framework:** https://osintframework.com/
- **VirusTotal Docs:** https://developers.virustotal.com/
- **ExifTool Manual:** https://exiftool.org/
- **Flask Docs:** https://flask.palletsprojects.com/

---

**Making OSINT fast, accessible, and efficient.** 🚀

Ready to streamline your investigations?
Great.
