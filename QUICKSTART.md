# ⚡ A-GRADE OSINT - QUICK START

## 🎯 **What You Got:**
- **18 OSINT tools** (up from 11!)
- **File upload** → Auto hash → VirusTotal scan
- **ExifTool** metadata extraction
- **Google Dorking** generator
- **Dual IP checking** (AbuseIPDB + VirusTotal)
- **Result clearing** when switching tools
- **Export** investigation results
- **7 NEW tools**: Reverse IP, MAC lookup, Email OSINT, Wayback Machine, Crypto tracker, and more!

---

## 🚀 **3-Step Setup:**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. (Optional) Install ExifTool**
**macOS:**
```bash
brew install exiftool
```

**Linux:**
```bash
sudo apt-get install exiftool
```

**Windows:**
Download from: https://exiftool.org/

### **3. Run It!**
```bash
python app.py
```

Open: **http://localhost:5000**

---

## 🔑 **API Keys (Optional)**

**3 APIs for full functionality:**
1. VirusTotal: https://www.virustotal.com/gui/join-us
2. AbuseIPDB: https://www.abuseipdb.com/register
3. HIBP: https://haveibeenpwned.com/API/Key

Add to `app.py` lines 35-45.

**Without API keys, 10+ tools still work!**

---

## ✨ **NEW Features You Requested:**

### ✅ **1. File Upload**
- Click "File Upload" in sidebar
- Select ANY file (up to 32MB)
- Get MD5 & SHA256 hashes instantly
- Automatic VirusTotal malware scan

### ✅ **2. ExifTool (Metadata)**
- Click "ExifTool" in sidebar
- Upload image/PDF/document
- Extract ALL metadata (GPS, camera, dates, etc.)

### ✅ **3. IP Reputation (Enhanced)**
- Now checks BOTH AbuseIPDB AND VirusTotal
- Dual-source verification
- More accurate threat detection

### ✅ **4. Result Clearing**
- Switch between tools → Previous results disappear
- Clean investigation workflow
- No confusing leftover data

### ✅ **5. Google Dorking**
- Click "Google Dork" in sidebar
- Enter target domain
- Select category (Sensitive files, Documents, Social, etc.)
- Get ready-to-use dork queries with search links

### ✅ **6. Export Results**
- Click "💾 Export" button in sidebar
- Downloads all investigation results as JSON
- Professional reporting capability

---

## 🎯 **Try These First:**

### **Test File Upload:**
1. Create a text file on your computer
2. Go to "File Upload" tool
3. Upload it
4. See MD5/SHA256 hashes + VirusTotal scan

### **Test ExifTool:**
1. Take a photo with your phone
2. Go to "ExifTool" tool
3. Upload the photo
4. See GPS, camera model, timestamp, etc.

### **Test Google Dorking:**
1. Go to "Google Dork" tool
2. Enter: `github.com`
3. Select: "Sensitive"
4. Click "Generate Dorks"
5. Click any "Search Google" button

### **Test Dual IP Check:**
1. Go to "IP Reputation" tool
2. Enter: `8.8.8.8`
3. See results from BOTH AbuseIPDB AND VirusTotal
4. Compare the two sources!

---

## 📊 **Tool Categories:**

**File Analysis** (3 tools)
- File Upload, Hash Check, ExifTool

**Network** (5 tools)
- IP Reputation, Geolocation, Reverse IP, MAC Lookup, Shodan

**Domain** (5 tools)
- WHOIS, DNS, Subdomains, SSL, Wayback Machine

**People** (3 tools)
- Email OSINT, Breach Check, Username Search

**Advanced** (2 tools)
- Google Dorking, Crypto Tracker

---

## 🐛 **Troubleshooting:**

**"No module named..."**
```bash
pip install -r requirements.txt
```

**ExifTool not working?**
- Install ExifTool separately (see step 2)
- Without it, you get basic file info only

**File upload fails?**
- Check file size (max 32MB)
- All file types supported

**Results not clearing?**
- Make sure you're clicking menu items to switch tools
- Results clear automatically on tool switch

---

## 💡 **Pro Tips:**

1. **Use Export** - Save your investigation results!
2. **No API keys?** - Still get 10+ working tools
3. **ExifTool** - Install it for full metadata power
4. **Google Dorks** - Use "Sensitive" category for interesting finds
5. **Dual IP Check** - Compare AbuseIPDB vs VirusTotal results

---

## 🎓 **For Your Defense:**

**Highlight These Features:**
- File upload with automatic hashing
- ExifTool metadata extraction
- Multi-source IP verification
- Google Dorking automation
- Professional result export
- 18 comprehensive tools
- Clean UX with result clearing

---

## 📝 **All Your Changes Implemented:**

✅ File upload → MD5/SHA256 → VirusTotal  
✅ ExifTool metadata extraction  
✅ IP checks through VirusTotal too  
✅ Results clear when switching tools  
✅ Google Dorking tool added  
✅ Plus 7 more A-grade tools  

---

**You're ready to impress! 🎓🏆**

**Questions? Check README.md for full documentation!**
