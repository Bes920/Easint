"""
EASINT - Professional Intelligence Toolkit
✅ MODIFIED: Auto-save integrated for all OSINT tools
Enhanced with file uploads, ExifTool, Google Dorking, and advanced features
"""
from services.results_service import ResultsService  
from services.investigation_service import InvestigationService 
from flask import Flask, render_template, request, jsonify, send_file
import requests
import os
import json
import dns.resolver
import ssl
import socket
from datetime import datetime
import whois
import hashlib
from werkzeug.utils import secure_filename
import subprocess
import base64
from io import BytesIO
import csv
import textwrap
from dotenv import load_dotenv
from routes.ai_routes import ai_bp
# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.register_blueprint(ai_bp)
# Upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'exe', 'zip', 'rar'}
MAX_FILE_SIZE = 32 * 1024 * 1024  # 32MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =============================================================================
# CONFIGURATION - Add your API keys here
# =============================================================================

# Essential APIs
VIRUSTOTAL_API_KEY = os.getenv('VIRUSTOTAL_API_KEY', 'YOUR_API_KEY_HERE')
ABUSEIPDB_API_KEY = os.getenv('ABUSEIPDB_API_KEY', 'YOUR_API_KEY_HERE')
HIBP_API_KEY = os.getenv('HIBP_API_KEY', 'YOUR_API_KEY_HERE')

# Optional APIs for advanced features
SHODAN_API_KEY = os.getenv('SHODAN_API_KEY', 'YOUR_API_KEY_HERE')
HUNTER_API_KEY = os.getenv('HUNTER_API_KEY', 'YOUR_API_KEY_HERE')
BLOCKCHAIN_API_KEY = os.getenv('BLOCKCHAIN_API_KEY', 'YOUR_API_KEY_HERE')

# =============================================================================
# ROUTES
# =============================================================================

#ai_chat route is in routes/ai_routes.py for better organization
@app.route('/ai-test')
def ai_test_page():
    """AI chatbot test page"""
    return render_template('ai_test.html')



@app.route('/')
def index():
    """Homepage that explains the platform and directs users to the right workflow"""
    return render_template('home.html')


@app.route('/tools')
def tools_page():
    """Primary workspace containing all OSINT tools"""
    return render_template('index.html')


# =============================================================================
# FILE UPLOAD & HASH CHECKING
# ✅ MODIFIED: Auto-save enabled
# =============================================================================

@app.route('/upload-file', methods=['POST'])
def upload_file():
    """Upload file, calculate MD5/SHA256, and check with VirusTotal"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    investigation_id = request.form.get('investigation_id')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        try:
            # Read file content
            file_content = file.read()
            filename = secure_filename(file.filename)
            
            # Calculate hashes
            md5_hash = hashlib.md5(file_content).hexdigest()
            sha256_hash = hashlib.sha256(file_content).hexdigest()
            
            # Check with VirusTotal
            vt_result = check_file_hash(sha256_hash)
            
            result = {
                'filename': filename,
                'size': len(file_content),
                'md5': md5_hash,
                'sha256': sha256_hash,
                'virustotal': vt_result,
                'timestamp': datetime.now().isoformat()
            }
            
            # ✅ AUTO-SAVE TO DATABASE
            threat_level = ResultsService.determine_threat_level(result, 'file-upload')
            ResultsService.save_tool_result(
                tool_name='file-upload',
                target=filename,
                result_data=result,
                threat_level=threat_level,
                investigation_id=investigation_id
            )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': f'File processing failed: {str(e)}'}), 500


@app.route('/check-hash', methods=['POST'])
def check_hash():
    """Check if a file hash is malicious using VirusTotal"""
    data = request.get_json()
    file_hash = data.get('hash')
    investigation_id = data.get('investigation_id')
    
    if not file_hash:
        return jsonify({'error': 'No file hash provided'}), 400
    
    if not is_valid_hash(file_hash):
        return jsonify({'error': 'Invalid hash format (use MD5, SHA1, or SHA256)'}), 400
    
    try:
        result = check_file_hash(file_hash)
        
        # ✅ AUTO-SAVE TO DATABASE
        threat_level = ResultsService.determine_threat_level(result, 'hash-checker')
        ResultsService.save_tool_result(
            tool_name='hash-checker',
            target=file_hash,
            result_data=result,
            investigation_id=investigation_id,
            threat_level=threat_level
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# IP REPUTATION - ENHANCED WITH VIRUSTOTAL
# ✅ MODIFIED: Auto-save enabled
# =============================================================================

@app.route('/check-ip', methods=['POST'])
def check_ip():
    """Check IP with both AbuseIPDB and VirusTotal"""
    data = request.get_json()
    ip_address = data.get('ip')
    investigation_id = data.get('investigation_id')
    
    if not ip_address:
        return jsonify({'error': 'No IP address provided'}), 400
    
    if not is_valid_ip(ip_address):
        return jsonify({'error': 'Invalid IP address format'}), 400
    
    try:
        # Check with AbuseIPDB
        abuseipdb_result = check_ip_reputation(ip_address)
        
        # Check with VirusTotal
        virustotal_result = check_ip_virustotal(ip_address)
        
        # Combine results
        result = {
            'ip': ip_address,
            'abuseipdb': abuseipdb_result,
            'virustotal': virustotal_result,
            'timestamp': datetime.now().isoformat()
        }
        
        # ✅ AUTO-SAVE TO DATABASE
        threat_level = ResultsService.determine_threat_level(result, 'ip-checker')
        ResultsService.save_tool_result(
            tool_name='ip-checker',
            target=ip_address,
            result_data=result,
            investigation_id=investigation_id,
            threat_level=threat_level
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# EXIFTOOL - METADATA EXTRACTION
# ✅ MODIFIED: Auto-save enabled
# =============================================================================

@app.route('/extract-exif', methods=['POST'])
def extract_exif():
    """Extract metadata from uploaded file using ExifTool"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    investigation_id = request.form.get('investigation_id')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract metadata
        metadata = extract_file_metadata(filepath)
        
        # Clean up
        os.remove(filepath)
        
        result = {
            'filename': filename,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }
        
        # ✅ AUTO-SAVE TO DATABASE
        ResultsService.save_tool_result(
            tool_name='exif-extraction',
            target=filename,
            result_data=result,
            investigation_id=investigation_id,
            threat_level='low'
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Metadata extraction failed: {str(e)}'}), 500


# =============================================================================
# GOOGLE DORKING
# ✅ MODIFIED: Auto-save enabled
# =============================================================================

@app.route('/google-dork', methods=['POST'])
def google_dork():
    """Generate Google dork queries"""
    data = request.get_json()
    target = data.get('target')
    dork_type = data.get('dork_type', 'general')
    investigation_id = data.get('investigation_id')
    
    if not target:
        return jsonify({'error': 'No target provided'}), 400
    
    try:
        result = generate_google_dorks(target, dork_type)
        
        # ✅ AUTO-SAVE TO DATABASE
        ResultsService.save_tool_result(
            tool_name='google-dork',
            target=target,
            result_data=result,
            investigation_id=investigation_id,
            threat_level='low'
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# ADVANCED TOOLS
# ✅ MODIFIED: Auto-save enabled
# =============================================================================

@app.route('/shodan-search', methods=['POST'])
def shodan_search():
    """Search Shodan for IP/domain information"""
    data = request.get_json()
    query = data.get('query')
    investigation_id = data.get('investigation_id')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        result = search_shodan(query)
        
        # ✅ AUTO-SAVE TO DATABASE
        ResultsService.save_tool_result(
            tool_name='shodan-search',
            target=query,
            result_data=result,
            investigation_id=investigation_id,
            threat_level='low'
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/reverse-ip', methods=['POST'])
def reverse_ip():
    """Find all domains hosted on an IP"""
    data = request.get_json()
    ip_address = data.get('ip')
    investigation_id = data.get('investigation_id')
    
    if not ip_address:
        return jsonify({'error': 'No IP provided'}), 400
    
    try:
        result = reverse_ip_lookup(ip_address)
        
        # ✅ AUTO-SAVE TO DATABASE
        ResultsService.save_tool_result(
            tool_name='reverse-ip',
            target=ip_address,
            result_data=result,
            investigation_id=investigation_id,
            threat_level='low'
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/email-osint', methods=['POST'])
def email_osint():
    """Comprehensive email OSINT"""
    data = request.get_json()
    email = data.get('email')
    investigation_id = data.get('investigation_id')
    
    if not email:
        return jsonify({'error': 'No email provided'}), 400
    
    try:
        result = comprehensive_email_osint(email)
        
        # ✅ AUTO-SAVE TO DATABASE
        threat_level = ResultsService.determine_threat_level(result, 'email-osint')
        ResultsService.save_tool_result(
            tool_name='email-osint',
            target=email,
            result_data=result,
            investigation_id=investigation_id,
            threat_level=threat_level
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/wayback-machine', methods=['POST'])
def wayback_machine():
    """Check Wayback Machine for archived snapshots"""
    data = request.get_json()
    url = data.get('url')
    investigation_id = data.get('investigation_id')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        result = check_wayback_machine(url)
        
        # ✅ AUTO-SAVE TO DATABASE
        ResultsService.save_tool_result(
            tool_name='wayback-machine',
            target=url,
            result_data=result,
            investigation_id=investigation_id,
            threat_level='low'
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/crypto-tracker', methods=['POST'])
def crypto_tracker():
    """Track cryptocurrency address"""
    data = request.get_json()
    address = data.get('address')
    crypto_type = data.get('type', 'btc')
    investigation_id = data.get('investigation_id')
    
    if not address:
        return jsonify({'error': 'No address provided'}), 400
    
    try:
        result = track_crypto_address(address, crypto_type)
        
        # ✅ AUTO-SAVE TO DATABASE
        ResultsService.save_tool_result(
            tool_name='crypto-tracker',
            target=address,
            result_data=result,
            investigation_id=investigation_id,
            threat_level='low'
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/mac-lookup', methods=['POST'])
def mac_lookup():
    """Lookup MAC address vendor"""
    data = request.get_json()
    mac = data.get('mac')
    investigation_id = data.get('investigation_id')
    
    if not mac:
        return jsonify({'error': 'No MAC address provided'}), 400
    
    try:
        result = lookup_mac_address(mac)
        
        # ✅ AUTO-SAVE TO DATABASE
        ResultsService.save_tool_result(
            tool_name='mac-lookup',
            target=mac,
            result_data=result,
            investigation_id=investigation_id,
            threat_level='low'
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/export-results', methods=['POST'])
def export_results():
    """Export investigation results in supported formats"""
    data = request.get_json()
    results = data.get('results', {})
    format_type = data.get('format', 'csv')
    investigation = data.get('investigation', {})
    analysis_summary = data.get('analysis_summary', {})
    
    
    if not results and not investigation.get('results'):
        return jsonify({'error': 'No results to export'}), 400
    
    try:
        if format_type == 'csv':
            csv_data = convert_to_csv(results)
            return jsonify({
                'format': 'csv',
                'data': csv_data,
                'timestamp': datetime.now().isoformat()
            })
        elif format_type == 'pdf':
            pdf_bytes = generate_investigation_pdf(investigation, analysis_summary)
            filename = build_export_filename(investigation.get('name'), 'pdf')

            return send_file(
                BytesIO(pdf_bytes),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            return jsonify({'error': 'Unsupported format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# EXISTING TOOL ROUTES
# ✅ MODIFIED: Auto-save enabled for all
# =============================================================================

@app.route('/whois-lookup', methods=['POST'])
def whois_lookup():
    """Perform WHOIS lookup"""
    data = request.get_json()
    domain = data.get('domain')
    investigation_id = data.get('investigation_id')
    
    if not domain:
        return jsonify({'error': 'No domain provided'}), 400
    
    try:
        result = perform_whois_lookup(domain)
        
        # ✅ AUTO-SAVE TO DATABASE
        ResultsService.save_tool_result(
            tool_name='whois-lookup',
            target=domain,
            result_data=result,
            investigation_id=investigation_id,
            threat_level='low'
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/email-breach', methods=['POST'])
def email_breach():
    """Check if email has been in a data breach"""
    data = request.get_json()
    email = data.get('email')
    investigation_id = data.get('investigation_id')
    
    if not email:
        return jsonify({'error': 'No email provided'}), 400
    
    try:
        result = check_email_breach(email)
        
        # ✅ AUTO-SAVE TO DATABASE
        threat_level = 'high' if result.get('breached') else 'safe'
        ResultsService.save_tool_result(
            tool_name='email-breach',
            target=email,
            result_data=result,
            investigation_id=investigation_id,
            threat_level=threat_level
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/username-search', methods=['POST'])
def username_search():
    """Search for username across platforms"""
    data = request.get_json()
    username = data.get('username')
    investigation_id = data.get('investigation_id')
    
    if not username:
        return jsonify({'error': 'No username provided'}), 400
    
    try:
        result = search_username(username)
        
        # ✅ AUTO-SAVE TO DATABASE
        ResultsService.save_tool_result(
            tool_name='username-search',
            target=username,
            result_data=result,
            investigation_id=investigation_id,
            threat_level='low'
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/subdomain-enum', methods=['POST'])
def subdomain_enum():
    """Enumerate subdomains"""
    data = request.get_json()
    domain = data.get('domain')
    investigation_id = data.get('investigation_id')
    
    if not domain:
        return jsonify({'error': 'No domain provided'}), 400
    
    try:
        result = enumerate_subdomains(domain)
        
        # ✅ AUTO-SAVE TO DATABASE
        ResultsService.save_tool_result(
            tool_name='subdomain-enum',
            target=domain,
            result_data=result,
            investigation_id=investigation_id,
            threat_level='low'
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/dns-lookup', methods=['POST'])
def dns_lookup():
    """Perform DNS lookup"""
    data = request.get_json()
    domain = data.get('domain')
    investigation_id = data.get('investigation_id')
    
    if not domain:
        return jsonify({'error': 'No domain provided'}), 400
    
    try:
        result = perform_dns_lookup(domain)
        
        # ✅ AUTO-SAVE TO DATABASE
        ResultsService.save_tool_result(
            tool_name='dns-lookup',
            target=domain,
            result_data=result,
            investigation_id=investigation_id,
            threat_level='low'
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ssl-info', methods=['POST'])
def ssl_info():
    """Get SSL certificate information"""
    data = request.get_json()
    domain = data.get('domain')
    investigation_id = data.get('investigation_id')
    
    if not domain:
        return jsonify({'error': 'No domain provided'}), 400
    
    try:
        result = get_ssl_info(domain)
        
        # ✅ AUTO-SAVE TO DATABASE
        threat_level = 'safe' if result.get('valid') else 'medium'
        ResultsService.save_tool_result(
            tool_name='ssl-info',
            target=domain,
            result_data=result,
            investigation_id=investigation_id,
            threat_level=threat_level
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/geolocate-ip', methods=['POST'])
def geolocate_ip():
    """Get IP geolocation"""
    data = request.get_json()
    ip_address = data.get('ip')
    investigation_id = data.get('investigation_id')
    
    if not ip_address:
        return jsonify({'error': 'No IP address provided'}), 400
    
    try:
        result = get_ip_geolocation(ip_address)
        
        # ✅ AUTO-SAVE TO DATABASE
        ResultsService.save_tool_result(
            tool_name='ip-geolocation',
            target=ip_address,
            result_data=result,
            investigation_id=investigation_id,
            threat_level='low'
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/phone-lookup', methods=['POST'])
def phone_lookup():
    """Lookup phone number information"""
    data = request.get_json()
    phone = data.get('phone')
    investigation_id = data.get('investigation_id')
    
    if not phone:
        return jsonify({'error': 'No phone number provided'}), 400
    
    try:
        result = lookup_phone_number(phone)
        
        # ✅ AUTO-SAVE TO DATABASE
        ResultsService.save_tool_result(
            tool_name='phone-lookup',
            target=phone,
            result_data=result,
            investigation_id=investigation_id,
            threat_level='low'
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/opsec')
def opsec():
    """OPSEC Education page"""
    return render_template('opsec.html')


# =============================================================================
# HELPER FUNCTIONS (UNCHANGED)
# =============================================================================

def check_ip_reputation(ip):
    if ABUSEIPDB_API_KEY == 'YOUR_API_KEY_HERE':
        return {'demo_mode': True, 'message': 'Add AbuseIPDB API key'}
    
    url = 'https://api.abuseipdb.com/api/v2/check'
    headers = {'Key': ABUSEIPDB_API_KEY, 'Accept': 'application/json'}
    params = {'ipAddress': ip, 'maxAgeInDays': '90'}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()['data']
        return {
            'abuse_score': data.get('abuseConfidenceScore', 0),
            'is_malicious': data.get('abuseConfidenceScore', 0) > 50,
            'total_reports': data.get('totalReports', 0),
            'last_reported': data.get('lastReportedAt')
        }
    except:
        return {'error': 'AbuseIPDB check failed'}


def check_ip_virustotal(ip):
    if VIRUSTOTAL_API_KEY == 'YOUR_API_KEY_HERE':
        return {'demo_mode': True, 'message': 'Add VirusTotal API key'}
    
    url = f'https://www.virustotal.com/api/v3/ip_addresses/{ip}'
    headers = {'x-apikey': VIRUSTOTAL_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()['data']['attributes']
        stats = data.get('last_analysis_stats', {})
        return {
            'detections': stats.get('malicious', 0),
            'is_malicious': stats.get('malicious', 0) > 0,
            'clean': stats.get('harmless', 0),
            'country': data.get('country')
        }
    except:
        return {'error': 'VirusTotal check failed'}


def check_file_hash(file_hash):
    if VIRUSTOTAL_API_KEY == 'YOUR_API_KEY_HERE':
        return {'demo_mode': True, 'message': 'Add VirusTotal API key', 'found': False}
    
    url = f'https://www.virustotal.com/api/v3/files/{file_hash}'
    headers = {'x-apikey': VIRUSTOTAL_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 404:
            return {'found': False, 'message': 'Hash not found in VirusTotal database'}
        
        data = response.json()['data']['attributes']
        stats = data.get('last_analysis_stats', {})
        return {
            'found': True,
            'detections': stats.get('malicious', 0),
            'total_scanners': sum(stats.values()),
            'is_malicious': stats.get('malicious', 0) > 0,
            'file_type': data.get('type_description'),
            'size': data.get('size'),
            'first_seen': data.get('first_submission_date')
        }
    except:
        return {'error': 'VirusTotal check failed', 'found': False}


def extract_file_metadata(filepath):
    try:
        result = subprocess.run(['exiftool', '-j', filepath], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            metadata = json.loads(result.stdout)[0]
            return {k: v for k, v in metadata.items() if not k.startswith('ExifTool')}
        else:
            return {'note': 'ExifTool not installed or failed'}
    except:
        return {'note': 'ExifTool not available - install with: sudo apt install exiftool'}


def generate_google_dorks(target, dork_type):
    dorks = {
        'general': [
            f'site:{target}',
            f'site:{target} filetype:pdf',
            f'site:{target} filetype:doc OR filetype:docx',
            f'site:{target} inurl:admin',
        ],
        'sensitive': [
            f'site:{target} filetype:env',
            f'site:{target} filetype:sql',
            f'site:{target} filetype:log',
            f'site:{target} inurl:config',
        ],
        'social': [
            f'"{target}" site:linkedin.com',
            f'"{target}" site:twitter.com',
            f'"{target}" site:facebook.com',
        ],
        'documents': [
            f'site:{target} filetype:xls OR filetype:xlsx',
            f'site:{target} filetype:ppt OR filetype:pptx',
            f'site:{target} filetype:txt',
        ]
    }
    
    selected_dorks = dorks.get(dork_type, dorks['general'])
    
    return {
        'target': target,
        'dork_type': dork_type,
        'dorks': selected_dorks,
        'google_url_base': 'https://www.google.com/search?q=',
        'timestamp': datetime.now().isoformat()
    }


def search_shodan(query):
    return {'demo_mode': True, 'message': 'Shodan integration requires API key', 'query': query}


def reverse_ip_lookup(ip):
    try:
        url = f'https://api.hackertarget.com/reverseiplookup/?q={ip}'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            domains = response.text.strip().split('\n')
            return {
                'ip': ip,
                'domains_found': len(domains),
                'domains': domains[:10],
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {'ip': ip, 'domains_found': 0, 'domains': [], 'message': 'No domains found'}
    except:
        return {'error': 'Reverse IP lookup failed'}


def comprehensive_email_osint(email):
    result = {
        'email': email,
        'timestamp': datetime.now().isoformat()
    }
    
    # Extract domain
    domain = email.split('@')[1] if '@' in email else None
    result['domain'] = domain
    
    # Check format validity
    result['valid_format'] = '@' in email and '.' in email
    
    # Domain MX records
    if domain:
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            result['mx_records'] = [str(r.exchange) for r in mx_records]
            result['email_server_exists'] = True
        except:
            result['mx_records'] = []
            result['email_server_exists'] = False
    
    return result


def check_wayback_machine(url):
    """Check Wayback Machine for historical snapshots"""
    try:
        api_url = f'http://archive.org/wayback/available?url={url}'
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        if data.get('archived_snapshots'):
            closest = data['archived_snapshots'].get('closest', {})
            return {
                'url': url,
                'archived': True,
                'snapshot_url': closest.get('url'),
                'snapshot_date': closest.get('timestamp'),
                'status': closest.get('status'),
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'url': url,
                'archived': False,
                'message': 'No snapshots found',
                'timestamp': datetime.now().isoformat()
            }
    except:
        return {'error': 'Wayback Machine check failed'}


def track_crypto_address(address, crypto_type):
    """Track cryptocurrency address (demo)"""
    return {
        'demo_mode': True,
        'address': address,
        'type': crypto_type,
        'message': 'Crypto tracking requires Blockchain.com API or similar service',
        'note': 'Would show: balance, transactions, first/last seen',
        'timestamp': datetime.now().isoformat()
    }


def lookup_mac_address(mac):
    """Lookup MAC address vendor"""
    try:
        # Clean MAC address
        mac_clean = mac.replace(':', '').replace('-', '').upper()[:6]
        
        # Use macvendors.com API
        url = f'https://api.macvendors.com/{mac}'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return {
                'mac': mac,
                'vendor': response.text,
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'mac': mac,
                'vendor': 'Unknown',
                'message': 'Vendor not found',
                'timestamp': datetime.now().isoformat()
            }
    except:
        return {'error': 'MAC lookup failed'}


def convert_to_csv(results):
    """Convert results to CSV format"""
    output = []
    for key, value in results.items():
        output.append(f'{key},{value}')
    return '\n'.join(output)


def build_export_filename(name, extension):
    """Build a safe export filename."""
    safe_name = secure_filename(name or 'investigation-report').strip()
    if not safe_name:
        safe_name = 'investigation-report'
    return f'{safe_name}.{extension}'


def generate_investigation_pdf(investigation, analysis_summary=None):
    """Generate a structured PDF report without external dependencies."""
    if not investigation:
        raise ValueError('No investigation data provided')

    results = investigation.get('results') or []
    if not results:
        raise ValueError('No results to export')

    if not has_exportable_analysis(analysis_summary):
        raise ValueError('Run AI analysis before exporting this investigation.')

    lines = build_pdf_report_lines(investigation, results, analysis_summary)
    pages = paginate_pdf_lines(lines)
    return render_pdf_document(pages)


def build_pdf_report_lines(investigation, results, analysis_summary):
    """Create the report content as wrapped text lines."""
    threat_counts = {}
    for result in results:
        level = (result.get('threat_level') or 'unknown').lower()
        threat_counts[level] = threat_counts.get(level, 0) + 1

    lines = [
        'EASINT Investigation Report',
        '[[DIVIDER]]',
        '',
        f"Investigation: {investigation.get('name') or 'Untitled Investigation'}",
        f"Status: {(investigation.get('status') or 'unknown').title()}",
        f"Description: {investigation.get('description') or 'N/A'}",
        f"Created: {format_export_datetime(investigation.get('created_at'))}",
        f"Updated: {format_export_datetime(investigation.get('updated_at'))}",
        f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Tags: {', '.join(investigation.get('tags') or []) or 'None'}",
        '',
        'Summary',
        f'Total results: {len(results)}',
        f"Threat distribution: {format_threat_counts(threat_counts)}",
        '',
        '[[DIVIDER]]',
        '',
        'AI Investigation Analysis',
        f"Overall threat: {(analysis_summary.get('overall_threat') or 'unknown').upper()}",
        f"Analyzed at: {format_export_datetime(investigation.get('aiAnalyzedAt'))}",
        ''
    ]

    lines.extend(build_analysis_section_lines('Executive Summary', analysis_summary.get('summary')))
    lines.extend(build_analysis_section_lines('Key Insights', analysis_summary.get('insights')))
    lines.extend(build_analysis_section_lines('Correlations', analysis_summary.get('correlations')))
    lines.extend(build_analysis_section_lines('Recommended Actions', analysis_summary.get('actions')))

    lines.extend([
        '[[DIVIDER]]',
        '',
        'Detailed Results',
        ''
    ])

    for index, result in enumerate(results, 1):
        lines.extend(build_result_section_lines(index, result))

    wrapped_lines = []
    for line in lines:
        wrapped = textwrap.wrap(
            stringify_export_value(line),
            width=92,
            replace_whitespace=False,
            drop_whitespace=False
        )
        wrapped_lines.extend(wrapped or [''])

    return wrapped_lines


def has_exportable_analysis(analysis_summary):
    """Check whether AI analysis data is present for export."""
    if not analysis_summary:
        return False

    return any(
        analysis_summary.get(key)
        for key in ['summary', 'insights', 'correlations', 'actions']
    )


def build_analysis_section_lines(title, content):
    """Format one AI analysis section."""
    lines = [title]
    section_lines = normalize_multiline_content(content)
    if section_lines:
        lines.extend(indent_export_lines(section_lines))
    else:
        lines.extend(indent_export_lines(['No information available']))
    lines.append('')
    return lines


def build_result_section_lines(index, result):
    """Format one investigation result for export."""
    result_data = result.get('result_data')
    lines = [
        '[[DIVIDER]]',
        f'Result {index}',
        f"Tool: {result.get('tool_name') or 'Unknown'}",
        f"Target: {result.get('target') or 'N/A'}",
        f"Threat level: {(result.get('threat_level') or 'unknown').upper()}",
        f"Captured: {format_export_datetime(result.get('created_at'))}",
    ]

    ai_analysis = result.get('ai_analysis')
    if ai_analysis:
        lines.append('Tool-specific AI notes:')
        lines.extend(indent_export_lines(normalize_multiline_content(ai_analysis)))

    highlights = extract_result_highlights(result_data)
    if highlights:
        lines.append('Key findings:')
        lines.extend(indent_export_lines(highlights))

    lines.append('Structured details:')
    lines.extend(indent_export_lines(format_result_data_for_export(result_data)))
    lines.append('')
    return lines


def format_export_datetime(value):
    """Format datetimes consistently for exports."""
    if not value:
        return 'N/A'

    try:
        normalized = str(value).replace('Z', '+00:00')
        return datetime.fromisoformat(normalized).strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return str(value)


def format_threat_counts(threat_counts):
    """Create a readable threat summary."""
    if not threat_counts:
        return 'None'

    priority = ['critical', 'high', 'medium', 'low', 'safe', 'unknown']
    parts = []
    for level in priority:
        if level in threat_counts:
            parts.append(f'{level.upper()}: {threat_counts[level]}')
    return ', '.join(parts)


def format_result_data_for_export(result_data):
    """Turn nested tool result data into readable export text."""
    if result_data in (None, '', {}, []):
        return ['No structured result data available']

    lines = summarize_export_data(result_data)
    return lines or ['No structured result data available']


def summarize_export_data(value, prefix=''):
    """Recursively convert structured data into readable lines."""
    if isinstance(value, dict):
        if not value:
            return [f'{prefix}No details available' if prefix else 'No details available']

        lines = []
        for key in sorted(value.keys()):
            formatted_key = humanize_export_key(key)
            item = value[key]

            if is_simple_export_value(item):
                lines.append(f'{formatted_key}: {format_simple_export_value(item)}')
                continue

            if isinstance(item, list) and all(is_simple_export_value(entry) for entry in item):
                lines.append(f'{formatted_key}: {format_simple_export_value(item)}')
                continue

            lines.append(f'{formatted_key}:')
            child_lines = summarize_export_data(item, prefix=f'{prefix}  ')
            lines.extend(indent_export_lines(child_lines))

        return lines

    if isinstance(value, list):
        if not value:
            return ['No items available']

        if all(is_simple_export_value(entry) for entry in value):
            return [f'- {format_simple_export_value(entry)}' for entry in value]

        lines = []
        for index, entry in enumerate(value, 1):
            if is_simple_export_value(entry):
                lines.append(f'- {format_simple_export_value(entry)}')
            else:
                lines.append(f'Item {index}:')
                lines.extend(indent_export_lines(summarize_export_data(entry, prefix=f'{prefix}  ')))
        return lines

    return [format_simple_export_value(value)]


def extract_result_highlights(result_data):
    """Extract a concise set of notable findings from top-level result data."""
    if not isinstance(result_data, dict):
        return []

    highlights = []
    for key in sorted(result_data.keys()):
        value = result_data[key]
        if isinstance(value, dict):
            nested_scalars = [
                f"{humanize_export_key(nested_key)}: {format_simple_export_value(nested_value)}"
                for nested_key, nested_value in sorted(value.items())
                if is_simple_export_value(nested_value) and nested_value not in (None, '', [], {})
            ]
            if nested_scalars:
                highlights.append(f"{humanize_export_key(key)} -> {'; '.join(nested_scalars[:3])}")
            continue

        if isinstance(value, list):
            if value and all(is_simple_export_value(item) for item in value):
                preview = ', '.join(format_simple_export_value(item) for item in value[:4])
                if len(value) > 4:
                    preview += f', +{len(value) - 4} more'
                highlights.append(f"{humanize_export_key(key)}: {preview}")
            continue

        if is_simple_export_value(value) and value not in (None, '', False):
            highlights.append(f"{humanize_export_key(key)}: {format_simple_export_value(value)}")

    return highlights[:8]


def normalize_multiline_content(content):
    """Convert free-form text into simple export lines."""
    if not content:
        return []

    lines = []
    for raw_line in stringify_export_value(content).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(('- ', '* ', '• ')):
            lines.append(line)
        else:
            lines.append(line)
    return lines


def humanize_export_key(key):
    """Convert snake_case or machine keys into labels."""
    text = stringify_export_value(key).replace('_', ' ').replace('-', ' ').strip()
    if not text:
        return 'Value'
    return ' '.join(word.capitalize() for word in text.split())


def is_simple_export_value(value):
    """Return True for scalar export values."""
    return isinstance(value, (str, int, float, bool)) or value is None


def format_simple_export_value(value):
    """Format scalar values for export readability."""
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    if value is None:
        return 'N/A'
    if isinstance(value, list):
        return ', '.join(format_simple_export_value(item) for item in value)
    return stringify_export_value(value)


def indent_export_lines(lines):
    """Indent detail lines for readability."""
    return [f'  {line}' if line else '' for line in lines]


def stringify_export_value(value):
    """Normalize values to export-safe strings."""
    if value is None:
        return ''
    if isinstance(value, str):
        return value.replace('\t', '    ')
    return str(value)


def paginate_pdf_lines(lines, max_lines_per_page=48):
    """Split report lines across PDF pages."""
    if not lines:
        return [[]]

    return [
        lines[index:index + max_lines_per_page]
        for index in range(0, len(lines), max_lines_per_page)
    ]


def render_pdf_document(pages):
    """Render plain text pages into a minimal PDF document."""
    page_width = 612
    page_height = 792
    left_margin = 50
    top_margin = 742

    page_entries = []
    for page_lines in pages:
        content_stream = build_pdf_content_stream(
            page_lines,
            left_margin=left_margin,
            top_margin=top_margin
        )
        page_entries.append(content_stream)

    total_objects = 4 + (2 * len(page_entries))
    body_font_object_id = total_objects - 1
    heading_font_object_id = total_objects
    page_object_ids = [4 + (index * 2) for index in range(len(page_entries))]
    content_object_ids = [3 + (index * 2) for index in range(len(page_entries))]

    pdf_objects = [
        '<< /Type /Catalog /Pages 2 0 R >>',
        f"<< /Type /Pages /Kids [{' '.join(f'{page_id} 0 R' for page_id in page_object_ids)}] /Count {len(page_object_ids)} >>"
    ]

    for index, content_stream in enumerate(page_entries):
        stream_bytes = content_stream.encode('latin-1', errors='replace')
        pdf_objects.append(
            f"<< /Length {len(stream_bytes)} >>\nstream\n{content_stream}\nendstream"
        )
        pdf_objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_width} {page_height}] "
            f"/Resources << /Font << /F1 {body_font_object_id} 0 R /F2 {heading_font_object_id} 0 R >> >> "
            f"/Contents {content_object_ids[index]} 0 R >>"
        )

    pdf_objects.append('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
    pdf_objects.append('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>')

    return assemble_pdf(pdf_objects)


def build_pdf_content_stream(lines, left_margin=50, top_margin=742):
    """Create a PDF text content stream."""
    stream_lines = ['BT']
    current_y = top_margin

    for line in lines:
        style = get_pdf_line_style(line)
        if style.get('divider'):
            current_y -= style.get('space_before', 0)
            stream_lines.extend(
                build_pdf_divider_commands(
                    current_y=current_y,
                    left_margin=left_margin,
                    width=512,
                    color=style.get('color', (0.82, 0.85, 0.90))
                )
            )
            current_y -= style['line_height']
            continue

        escaped = escape_pdf_text(line)
        red, green, blue = style.get('color', (0.12, 0.16, 0.22))
        stream_lines.append(f'{red:.3f} {green:.3f} {blue:.3f} rg')
        stream_lines.append(f'/{style["font"]} {style["size"]} Tf')
        stream_lines.append(f'1 0 0 1 {left_margin + style["indent"]} {current_y} Tm ({escaped}) Tj')
        current_y -= style['line_height']

    stream_lines.append('ET')
    return '\n'.join(stream_lines)


def get_pdf_line_style(line):
    """Return PDF text styling for a line."""
    text = stringify_export_value(line).strip()

    if text == '[[DIVIDER]]':
        return {
            'divider': True,
            'line_height': 16,
            'space_before': 4,
            'color': (0.80, 0.84, 0.90)
        }

    if not text:
        return {'font': 'F1', 'size': 10, 'line_height': 10, 'indent': 0, 'color': (0.12, 0.16, 0.22)}

    if text == 'EASINT Investigation Report':
        return {'font': 'F2', 'size': 18, 'line_height': 24, 'indent': 0, 'color': (0.07, 0.18, 0.34)}

    if is_pdf_primary_heading(text):
        return {'font': 'F2', 'size': 13, 'line_height': 20, 'indent': 0, 'color': (0.10, 0.20, 0.38)}

    if is_pdf_secondary_heading(text):
        return {'font': 'F2', 'size': 11, 'line_height': 17, 'indent': 0, 'color': (0.18, 0.22, 0.30)}

    if text.startswith('Overall threat:'):
        threat_level = text.split(':', 1)[1].strip().lower()
        return {'font': 'F2', 'size': 11, 'line_height': 16, 'indent': 0, 'color': get_pdf_threat_color(threat_level)}

    if text.startswith('Threat level:'):
        threat_level = text.split(':', 1)[1].strip().lower()
        return {'font': 'F2', 'size': 10, 'line_height': 15, 'indent': 0, 'color': get_pdf_threat_color(threat_level)}

    if line.startswith('  '):
        return {'font': 'F1', 'size': 10, 'line_height': 13, 'indent': 12, 'color': (0.16, 0.18, 0.22)}

    return {'font': 'F1', 'size': 10, 'line_height': 14, 'indent': 0, 'color': (0.12, 0.16, 0.22)}


def is_pdf_primary_heading(text):
    """Return True if a line is a major report heading."""
    return text in {
        'Summary',
        'AI Investigation Analysis',
        'Executive Summary',
        'Key Insights',
        'Correlations',
        'Recommended Actions',
        'Detailed Results'
    }


def is_pdf_secondary_heading(text):
    """Return True if a line is a subsection heading."""
    return (
        text.startswith('Result ') or
        text in {'Tool-specific AI notes:', 'Key findings:', 'Structured details:'}
    )


def get_pdf_threat_color(level):
    """Return RGB color tuple for threat text."""
    colors = {
        'critical': (0.67, 0.10, 0.10),
        'high': (0.78, 0.32, 0.08),
        'medium': (0.71, 0.53, 0.05),
        'low': (0.14, 0.45, 0.20),
        'safe': (0.10, 0.42, 0.28),
        'unknown': (0.35, 0.38, 0.42)
    }
    return colors.get(level, colors['unknown'])


def build_pdf_divider_commands(current_y, left_margin=50, width=512, color=(0.82, 0.85, 0.90)):
    """Draw a thin divider line across the page."""
    red, green, blue = color
    return [
        'ET',
        f'{red:.3f} {green:.3f} {blue:.3f} RG',
        '0.8 w',
        f'{left_margin} {current_y} m {left_margin + width} {current_y} l S',
        'BT'
    ]


def escape_pdf_text(text):
    """Escape text for use in a PDF string literal."""
    return (
        stringify_export_value(text)
        .replace('\\', '\\\\')
        .replace('(', '\\(')
        .replace(')', '\\)')
    )


def assemble_pdf(pdf_objects):
    """Assemble PDF objects into a valid PDF byte stream."""
    output = ['%PDF-1.4\n']
    offsets = [0]
    current_offset = len(output[0].encode('latin-1'))

    for index, obj in enumerate(pdf_objects, 1):
        offsets.append(current_offset)
        object_text = f'{index} 0 obj\n{obj}\nendobj\n'
        output.append(object_text)
        current_offset += len(object_text.encode('latin-1'))

    xref_offset = current_offset
    output.append(f'xref\n0 {len(pdf_objects) + 1}\n')
    output.append('0000000000 65535 f \n')

    for offset in offsets[1:]:
        output.append(f'{offset:010d} 00000 n \n')

    output.append(
        f'trailer\n<< /Size {len(pdf_objects) + 1} /Root 1 0 R >>\n'
        f'startxref\n{xref_offset}\n%%EOF'
    )

    return ''.join(output).encode('latin-1', errors='replace')


# =============================================================================
# EXISTING FUNCTIONS (From previous version)
# =============================================================================

def perform_whois_lookup(domain):
    try:
        w = whois.whois(domain)
        return {
            'domain': domain,
            'registrar': w.registrar if hasattr(w, 'registrar') else 'Unknown',
            'creation_date': str(w.creation_date) if hasattr(w, 'creation_date') else 'Unknown',
            'expiration_date': str(w.expiration_date) if hasattr(w, 'expiration_date') else 'Unknown',
            'name_servers': w.name_servers if hasattr(w, 'name_servers') else [],
            'timestamp': datetime.now().isoformat()
        }
    except:
        return {'error': 'WHOIS lookup failed'}


def check_email_breach(email):
    if HIBP_API_KEY == 'YOUR_API_KEY_HERE':
        return {'demo_mode': True, 'message': 'Add HIBP API key'}
    
    url = f'https://haveibeenpwned.com/api/v3/breachedaccount/{email}'
    headers = {'hibp-api-key': HIBP_API_KEY, 'User-Agent': 'OSINT-Tool'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 404:
            return {'email': email, 'breached': False}
        breaches = response.json()
        return {'email': email, 'breached': True, 'breach_count': len(breaches), 'breaches': breaches}
    except:
        return {'error': 'Breach check failed'}


def search_username(username):
    platforms = {
        'GitHub': f'https://github.com/{username}',
        'Twitter/X': f'https://twitter.com/{username}',
        'Instagram': f'https://instagram.com/{username}',
        'Reddit': f'https://reddit.com/user/{username}',
        'LinkedIn': f'https://linkedin.com/in/{username}',
    }
    
    results = []
    for platform, url in platforms.items():
        try:
            response = requests.get(url, timeout=5)
            results.append({'platform': platform, 'url': url, 'exists': response.status_code == 200})
        except:
            results.append({'platform': platform, 'url': url, 'exists': False})
    
    return {'username': username, 'results': results}


def enumerate_subdomains(domain):
    common = ['www', 'mail', 'ftp', 'admin', 'blog', 'dev', 'api', 'test']
    found = []
    
    for sub in common:
        try:
            answers = dns.resolver.resolve(f'{sub}.{domain}', 'A')
            found.append({'subdomain': f'{sub}.{domain}', 'ips': [str(r) for r in answers]})
        except:
            pass
    
    return {'domain': domain, 'subdomains': found}


def perform_dns_lookup(domain):
    records = {}
    for rtype in ['A', 'AAAA', 'MX', 'NS', 'TXT']:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            records[rtype] = [str(r) for r in answers]
        except:
            records[rtype] = []
    return {'domain': domain, 'records': records}


def get_ssl_info(domain):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                return {
                    'domain': domain,
                    'issuer': dict(x[0] for x in cert['issuer']),
                    'valid': True,
                    'not_after': cert['notAfter']
                }
    except:
        return {'error': 'SSL check failed'}


def get_ip_geolocation(ip_address):
    try:
        url = f'http://ip-api.com/json/{ip_address}'
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get('status') == 'success':
            return {
                'ip': ip_address,
                'country': data.get('country'),
                'city': data.get('city'),
                'latitude': data.get('lat'),
                'longitude': data.get('lon'),
                'isp': data.get('isp')
            }
    except:
        pass
    return {'error': 'Geolocation failed'}


def lookup_phone_number(phone):
    return {'demo_mode': True, 'phone': phone, 'message': 'Phone lookup requires Twilio API'}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def is_valid_ip(ip):
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except:
        return False


def is_valid_hash(hash_value):
    hash_len = len(hash_value)
    if hash_len not in [32, 40, 64]:
        return False
    try:
        int(hash_value, 16)
        return True
    except:
        return False

# ===================================================================
# INVESTIGATION DASHBOARD API ROUTES
# Add these routes to your app.py
# ===================================================================

from flask import Flask, render_template, request, jsonify
from services.investigation_service import InvestigationService
from datetime import datetime

# =============================================================================
# DASHBOARD PAGE
# =============================================================================

@app.route('/dashboard')
def dashboard():
    """Investigation Dashboard page"""
    return render_template('dashboard.html')


# =============================================================================
# API ROUTES FOR INVESTIGATIONS
# =============================================================================

@app.route('/api/investigations', methods=['GET'])
def get_investigations():
    """Get all investigations with their result counts and threat levels"""
    try:
        # Get all investigations (user_id=None for development)
        investigations = InvestigationService.get_user_investigations(user_id=None)
        
        # Enhance each investigation with additional data
        for inv in investigations:
            try:
                # Get results for this investigation
                results = InvestigationService.get_investigation_results(inv['id'])
                inv['result_count'] = len(results)
                
                # Determine highest threat level
                if results:
                    threat_levels = []
                    for r in results:
                        if r.get('threat_level'):
                            threat_levels.append(r['threat_level'])
                    
                    if threat_levels:
                        threat_priority = {
                            'critical': 5, 
                            'high': 4, 
                            'medium': 3, 
                            'low': 2, 
                            'safe': 1
                        }
                        # Get the highest threat level
                        highest = max(threat_levels, key=lambda x: threat_priority.get(x, 0))
                        inv['threat_level'] = highest
                    else:
                        inv['threat_level'] = 'low'
                else:
                    inv['threat_level'] = 'low'
                    
            except Exception as e:
                print(f"⚠️ Error processing investigation {inv.get('id')}: {e}")
                inv['result_count'] = 0
                inv['threat_level'] = 'low'
        
        return jsonify({
            'success': True,
            'investigations': investigations
        })
        
    except Exception as e:
        print(f"❌ ERROR in get_investigations: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/investigations/<investigation_id>', methods=['GET'])
def get_investigation(investigation_id):
    """Get investigation details with all results"""
    try:
        investigation = InvestigationService.get_investigation_with_results(investigation_id)
        
        if not investigation:
            return jsonify({
                'success': False,
                'error': 'Investigation not found'
            }), 404
        
        # ✅ FIX: Wrap in success response
        return jsonify({
            'success': True,
            'investigation': investigation
        })
        
    except Exception as e:
        print(f"❌ ERROR in get_investigation: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
 
@app.route('/api/investigations/<investigation_id>/results', methods=['GET'])
def get_investigation_results(investigation_id):
    """Get all results for an investigation"""
    try:
        results = InvestigationService.get_investigation_results(investigation_id)
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        print(f"❌ ERROR in get_investigation_results: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/investigations', methods=['POST'])
def create_investigation():
    """Create a new investigation"""
    try:
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description', '')
        tags = data.get('tags', [])
        
        if not name:
            return jsonify({'error': 'Investigation name is required'}), 400
        
        # Create investigation
        investigation = InvestigationService.create_investigation(
            user_id=None,  # Will use real user ID after auth
            name=name,
            description=description,
            tags=tags
        )
        
        return jsonify({
            'success': True,
            'investigation': investigation
        })
        
    except Exception as e:
        print(f"❌ ERROR in create_investigation: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/investigations/<investigation_id>', methods=['PUT'])
def update_investigation(investigation_id):
    """Update investigation (status, description, etc.)"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if status and status in ['active', 'completed', 'archived']:
            success = InvestigationService.update_investigation_status(investigation_id, status)
            
            if success:
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'Failed to update investigation'}), 500
        else:
            return jsonify({'error': 'Invalid status'}), 400
            
    except Exception as e:
        print(f"❌ ERROR in update_investigation: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/investigations/<investigation_id>', methods=['DELETE'])
def delete_investigation_api(investigation_id):
    """Delete investigation and all its results"""
    try:
        success = InvestigationService.delete_investigation(investigation_id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to delete investigation'}), 500
            
    except Exception as e:
        print(f"❌ ERROR in delete_investigation_api: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500




# =============================================================================
# RUN THE APP
# =============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
