"""
OSINT A-Grade Platform - Professional Intelligence Toolkit
Enhanced with file uploads, ExifTool, Google Dorking, and advanced features
"""

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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

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

# Optional APIs for A-grade features
SHODAN_API_KEY = os.getenv('SHODAN_API_KEY', 'YOUR_API_KEY_HERE')
HUNTER_API_KEY = os.getenv('HUNTER_API_KEY', 'YOUR_API_KEY_HERE')
BLOCKCHAIN_API_KEY = os.getenv('BLOCKCHAIN_API_KEY', 'YOUR_API_KEY_HERE')

# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def index():
    """Home page with all OSINT tools"""
    return render_template('index.html')


# =============================================================================
# FILE UPLOAD & HASH CHECKING
# =============================================================================

@app.route('/upload-file', methods=['POST'])
def upload_file():
    """Upload file, calculate MD5/SHA256, and check with VirusTotal"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        try:
            # Read file content
            file_content = file.read()
            
            # Calculate hashes
            md5_hash = hashlib.md5(file_content).hexdigest()
            sha256_hash = hashlib.sha256(file_content).hexdigest()
            
            # Check with VirusTotal
            vt_result = check_file_hash(sha256_hash)
            
            return jsonify({
                'filename': secure_filename(file.filename),
                'size': len(file_content),
                'md5': md5_hash,
                'sha256': sha256_hash,
                'virustotal': vt_result,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({'error': f'File processing failed: {str(e)}'}), 500


@app.route('/check-hash', methods=['POST'])
def check_hash():
    """Check if a file hash is malicious using VirusTotal"""
    data = request.get_json()
    file_hash = data.get('hash')
    
    if not file_hash:
        return jsonify({'error': 'No file hash provided'}), 400
    
    if not is_valid_hash(file_hash):
        return jsonify({'error': 'Invalid hash format (use MD5, SHA1, or SHA256)'}), 400
    
    try:
        result = check_file_hash(file_hash)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# IP REPUTATION - ENHANCED WITH VIRUSTOTAL
# =============================================================================

@app.route('/check-ip', methods=['POST'])
def check_ip():
    """Check IP with both AbuseIPDB and VirusTotal"""
    data = request.get_json()
    ip_address = data.get('ip')
    
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
        combined = {
            'ip': ip_address,
            'abuseipdb': abuseipdb_result,
            'virustotal': virustotal_result,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(combined)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# EXIFTOOL - METADATA EXTRACTION
# =============================================================================

@app.route('/extract-exif', methods=['POST'])
def extract_exif():
    """Extract metadata from uploaded file using ExifTool"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
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
        
        return jsonify({
            'filename': filename,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Metadata extraction failed: {str(e)}'}), 500


# =============================================================================
# GOOGLE DORKING
# =============================================================================

@app.route('/google-dork', methods=['POST'])
def google_dork():
    """Generate Google dork queries"""
    data = request.get_json()
    target = data.get('target')
    dork_type = data.get('dork_type', 'general')
    
    if not target:
        return jsonify({'error': 'No target provided'}), 400
    
    try:
        dorks = generate_google_dorks(target, dork_type)
        return jsonify(dorks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# NEW A-GRADE TOOLS
# =============================================================================

@app.route('/shodan-search', methods=['POST'])
def shodan_search():
    """Search Shodan for IP/domain information"""
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        result = search_shodan(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/reverse-ip', methods=['POST'])
def reverse_ip():
    """Find all domains hosted on an IP"""
    data = request.get_json()
    ip_address = data.get('ip')
    
    if not ip_address:
        return jsonify({'error': 'No IP provided'}), 400
    
    try:
        result = reverse_ip_lookup(ip_address)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/email-osint', methods=['POST'])
def email_osint():
    """Comprehensive email OSINT"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'No email provided'}), 400
    
    try:
        result = perform_email_osint(email)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/wayback-machine', methods=['POST'])
def wayback_machine():
    """Check Wayback Machine for historical snapshots"""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        result = check_wayback_machine(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/crypto-tracker', methods=['POST'])
def crypto_tracker():
    """Track cryptocurrency wallet/address"""
    data = request.get_json()
    address = data.get('address')
    crypto_type = data.get('type', 'btc')
    
    if not address:
        return jsonify({'error': 'No address provided'}), 400
    
    try:
        result = track_crypto_address(address, crypto_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/mac-lookup', methods=['POST'])
def mac_lookup():
    """Lookup MAC address vendor"""
    data = request.get_json()
    mac = data.get('mac')
    
    if not mac:
        return jsonify({'error': 'No MAC address provided'}), 400
    
    try:
        result = lookup_mac_address(mac)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# EXPORT FUNCTIONALITY
# =============================================================================

@app.route('/export-results', methods=['POST'])
def export_results():
    """Export investigation results"""
    data = request.get_json()
    results = data.get('results')
    format_type = data.get('format', 'json')
    
    if not results:
        return jsonify({'error': 'No results to export'}), 400
    
    try:
        if format_type == 'json':
            output = json.dumps(results, indent=2)
            mimetype = 'application/json'
            filename = f'osint_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        elif format_type == 'csv':
            output = convert_to_csv(results)
            mimetype = 'text/csv'
            filename = f'osint_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        else:
            return jsonify({'error': 'Invalid format'}), 400
        
        return jsonify({
            'success': True,
            'data': output,
            'filename': filename,
            'message': 'Results exported successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# EXISTING TOOLS (From previous version)
# =============================================================================

@app.route('/whois-lookup', methods=['POST'])
def whois_lookup():
    data = request.get_json()
    domain = data.get('domain')
    if not domain:
        return jsonify({'error': 'No domain provided'}), 400
    try:
        result = perform_whois_lookup(domain)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/email-breach', methods=['POST'])
def email_breach():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'No email provided'}), 400
    try:
        result = check_email_breach(email)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/username-search', methods=['POST'])
def username_search():
    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({'error': 'No username provided'}), 400
    try:
        result = search_username(username)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/subdomain-enum', methods=['POST'])
def subdomain_enum():
    data = request.get_json()
    domain = data.get('domain')
    if not domain:
        return jsonify({'error': 'No domain provided'}), 400
    try:
        result = enumerate_subdomains(domain)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/dns-lookup', methods=['POST'])
def dns_lookup():
    data = request.get_json()
    domain = data.get('domain')
    if not domain:
        return jsonify({'error': 'No domain provided'}), 400
    try:
        result = perform_dns_lookup(domain)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ssl-info', methods=['POST'])
def ssl_info():
    data = request.get_json()
    domain = data.get('domain')
    if not domain:
        return jsonify({'error': 'No domain provided'}), 400
    try:
        result = get_ssl_info(domain)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/geolocate-ip', methods=['POST'])
def geolocate_ip():
    data = request.get_json()
    ip_address = data.get('ip')
    if not ip_address:
        return jsonify({'error': 'No IP provided'}), 400
    try:
        result = get_ip_geolocation(ip_address)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/phone-lookup', methods=['POST'])
def phone_lookup():
    data = request.get_json()
    phone = data.get('phone')
    if not phone:
        return jsonify({'error': 'No phone provided'}), 400
    try:
        result = lookup_phone_number(phone)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/opsec')
def opsec():
    return render_template('opsec.html')
# =============================================================================
# CORE OSINT FUNCTIONS
# =============================================================================

def check_file_hash(file_hash):
    """Query VirusTotal for file hash reputation"""
    if VIRUSTOTAL_API_KEY == 'YOUR_API_KEY_HERE':
        return {
            'demo_mode': True,
            'message': 'Demo data - add VirusTotal API key for real results',
            'hash': file_hash,
            'detections': 0,
            'total_scanners': 70,
            'is_malicious': False
        }
    
    url = f'https://www.virustotal.com/api/v3/files/{file_hash}'
    headers = {'x-apikey': VIRUSTOTAL_API_KEY}
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 404:
        return {
            'hash': file_hash,
            'found': False,
            'message': 'Hash not found in VirusTotal database',
            'timestamp': datetime.now().isoformat()
        }
    
    response.raise_for_status()
    data = response.json()
    
    attributes = data.get('data', {}).get('attributes', {})
    stats = attributes.get('last_analysis_stats', {})
    
    malicious = stats.get('malicious', 0)
    total = sum(stats.values())
    
    return {
        'hash': file_hash,
        'found': True,
        'detections': malicious,
        'total_scanners': total,
        'is_malicious': malicious > 0,
        'harmless': stats.get('harmless', 0),
        'suspicious': stats.get('suspicious', 0),
        'undetected': stats.get('undetected', 0),
        'timestamp': datetime.now().isoformat()
    }


def check_ip_reputation(ip_address):
    """Query AbuseIPDB for IP reputation"""
    if ABUSEIPDB_API_KEY == 'YOUR_API_KEY_HERE':
        return {
            'demo_mode': True,
            'message': 'Demo data - add AbuseIPDB API key',
            'abuse_score': 15,
            'reports': 3,
            'is_malicious': False
        }
    
    url = 'https://api.abuseipdb.com/api/v2/check'
    headers = {'Key': ABUSEIPDB_API_KEY, 'Accept': 'application/json'}
    params = {'ipAddress': ip_address, 'maxAgeInDays': 90}
    
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    ip_data = data.get('data', {})
    
    return {
        'abuse_score': ip_data.get('abuseConfidenceScore', 0),
        'reports': ip_data.get('totalReports', 0),
        'country': ip_data.get('countryCode', 'Unknown'),
        'isp': ip_data.get('isp', 'Unknown'),
        'is_malicious': ip_data.get('abuseConfidenceScore', 0) > 50,
        'last_reported': ip_data.get('lastReportedAt', 'Never')
    }


def check_ip_virustotal(ip_address):
    """Check IP address with VirusTotal"""
    if VIRUSTOTAL_API_KEY == 'YOUR_API_KEY_HERE':
        return {
            'demo_mode': True,
            'message': 'Demo - add VirusTotal API key',
            'detections': 0,
            'is_malicious': False
        }
    
    url = f'https://www.virustotal.com/api/v3/ip_addresses/{ip_address}'
    headers = {'x-apikey': VIRUSTOTAL_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        attributes = data.get('data', {}).get('attributes', {})
        stats = attributes.get('last_analysis_stats', {})
        
        malicious = stats.get('malicious', 0)
        
        return {
            'detections': malicious,
            'is_malicious': malicious > 0,
            'harmless': stats.get('harmless', 0),
            'suspicious': stats.get('suspicious', 0),
            'undetected': stats.get('undetected', 0)
        }
    except:
        return {'error': 'VirusTotal check failed'}


def extract_file_metadata(filepath):
    """Extract metadata using ExifTool or basic Python methods"""
    metadata = {}
    
    try:
        # Try using exiftool if installed
        result = subprocess.run(
            ['exiftool', '-json', filepath],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            exif_data = json.loads(result.stdout)[0]
            metadata = {k: str(v) for k, v in exif_data.items() if not k.startswith('SourceFile')}
        else:
            raise Exception("ExifTool not available")
            
    except:
        # Fallback to basic file info
        import os
        from datetime import datetime
        
        stat_info = os.stat(filepath)
        metadata = {
            'FileName': os.path.basename(filepath),
            'FileSize': f'{stat_info.st_size} bytes',
            'FileModifyDate': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            'FileAccessDate': datetime.fromtimestamp(stat_info.st_atime).isoformat(),
            'Note': 'Install ExifTool for detailed metadata extraction'
        }
    
    return metadata


def generate_google_dorks(target, dork_type):
    """Generate Google dork queries"""
    
    dork_categories = {
        'general': [
            f'site:{target}',
            f'site:{target} filetype:pdf',
            f'site:{target} filetype:doc',
            f'site:{target} filetype:xls',
            f'site:{target} inurl:admin',
            f'site:{target} inurl:login',
        ],
        'sensitive': [
            f'site:{target} filetype:sql',
            f'site:{target} filetype:env',
            f'site:{target} "index of /"',
            f'site:{target} intext:"password"',
            f'site:{target} filetype:log',
            f'site:{target} inurl:backup',
        ],
        'social': [
            f'"{target}" site:linkedin.com',
            f'"{target}" site:twitter.com',
            f'"{target}" site:facebook.com',
            f'"{target}" site:instagram.com',
        ],
        'documents': [
            f'site:{target} filetype:pdf',
            f'site:{target} filetype:doc OR filetype:docx',
            f'site:{target} filetype:xls OR filetype:xlsx',
            f'site:{target} filetype:ppt OR filetype:pptx',
            f'site:{target} filetype:txt',
        ]
    }
    
    selected_dorks = dork_categories.get(dork_type, dork_categories['general'])
    
    return {
        'target': target,
        'dork_type': dork_type,
        'dorks': selected_dorks,
        'google_url_base': 'https://www.google.com/search?q=',
        'count': len(selected_dorks),
        'timestamp': datetime.now().isoformat()
    }


def search_shodan(query):
    """Search Shodan (demo mode if no API key)"""
    if SHODAN_API_KEY == 'YOUR_API_KEY_HERE':
        return {
            'demo_mode': True,
            'message': 'Get Shodan API key from https://account.shodan.io/',
            'query': query,
            'note': 'Shodan provides: open ports, services, vulnerabilities, banners'
        }
    
    # Real Shodan implementation would go here
    return {
        'query': query,
        'message': 'Shodan integration ready - add your API key',
        'timestamp': datetime.now().isoformat()
    }


def reverse_ip_lookup(ip_address):
    """Find all domains on an IP (using ViewDNS API or similar)"""
    try:
        # Using HackerTarget free API
        url = f'https://api.hackertarget.com/reverseiplookup/?q={ip_address}'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            domains = response.text.strip().split('\n')
            if 'error' not in domains[0].lower():
                return {
                    'ip': ip_address,
                    'domains_found': len(domains),
                    'domains': domains[:50],  # Limit to 50
                    'timestamp': datetime.now().isoformat()
                }
        
        return {
            'ip': ip_address,
            'domains_found': 0,
            'message': 'No domains found or API limit reached',
            'timestamp': datetime.now().isoformat()
        }
    except:
        return {'error': 'Reverse IP lookup failed'}


def perform_email_osint(email):
    """Comprehensive email OSINT"""
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


# =============================================================================
# RUN THE APP
# =============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
