# 🔍 **EASINT** - Professional OSINT Intelligence Platform

> **18+ Investigation Tools | Production-Ready | For Security Researchers & Analysts**

A **professional-grade Open Source Intelligence (OSINT) platform** that replaces expensive, complex investigation workflows. Instead of juggling 5-10 different websites and tools, EASINT brings all 18+ OSINT capabilities into one unified interface. Designed for cybersecurity professionals, researchers, and analysts who need fast, reliable intelligence gathering.

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

---


- Results clear when switching tools
- No confusing leftover data
- Professional investigation workflow

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

1. **Copy the example configuration:**
```bash
cp .env.example .env
```

2. **Edit `.env` file and add your API keys:**
```
VIRUSTOTAL_API_KEY=your_key_here
ABUSEIPDB_API_KEY=your_key_here
HIBP_API_KEY=your_key_here
SHODAN_API_KEY=your_key_here
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

### **▶️ Step 4: Run the Application**

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

### **🌐 Step 5: Open in Browser**

Visit: **http://localhost:5000** 🎉

---

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
✅ No data persistence (privacy)  
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

- **Professional dark theme** - OSINT aesthetic
- **Sidebar navigation** - Easy tool switching
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
