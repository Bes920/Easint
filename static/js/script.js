/**
 * EASINT - Complete JavaScript
 * All 18 tools with proper handlers
 * ✅ MODIFIED: Added investigation selector support
 */

// ==========================================================================
// INVESTIGATION SELECTOR (NEW - Step 3A)
// ==========================================================================

// Load investigations for dropdown
async function loadInvestigationsDropdown() {
    try {
        const response = await fetch('/api/investigations');
        const data = await response.json();
        
        const dropdown = document.getElementById('currentInvestigation');
        
        if (data.success && data.investigations.length > 0) {
            dropdown.innerHTML = '';
            
            // Add "Auto-saved Results" as default
            const autoOption = document.createElement('option');
            autoOption.value = 'auto';
            autoOption.textContent = '📁 Auto-saved Results (Default)';
            dropdown.appendChild(autoOption);
            
            // Add all other investigations
            data.investigations.forEach(inv => {
                if (inv.name === 'Auto-saved Results') return;
                
                const option = document.createElement('option');
                option.value = inv.id;
                option.textContent = `📊 ${inv.name}`;
                dropdown.appendChild(option);
            });
            
            // Restore last selected
            const lastSelected = localStorage.getItem('selectedInvestigation');
            if (lastSelected) {
                dropdown.value = lastSelected;
            }
            
            // Save on change
            dropdown.addEventListener('change', function() {
                localStorage.setItem('selectedInvestigation', this.value);
                console.log(`✅ Results will save to: ${this.options[this.selectedIndex].text}`);
            });
            
        } else {
            dropdown.innerHTML = '<option value="auto">📁 Auto-saved Results (Default)</option>';
        }
        
    } catch (error) {
        console.error('Failed to load investigations:', error);
        const dropdown = document.getElementById('currentInvestigation');
        if (dropdown) {
            dropdown.innerHTML = '<option value="auto">📁 Auto-saved Results (Default)</option>';
        }
    }
}

// Get currently selected investigation ID
function getCurrentInvestigationId() {
    const dropdown = document.getElementById('currentInvestigation');
    if (!dropdown) return null;
    const value = dropdown.value;
    return (value === 'auto' || value === '') ? null : value;
}

document.addEventListener('DOMContentLoaded', function() {
    
    // Load investigation dropdown on page load
    if (document.getElementById('currentInvestigation')) {
        loadInvestigationsDropdown();
    }
    
    // ==========================================================================
    // NAVIGATION WITH RESULT CLEARING
    // ==========================================================================
    
    const menuItems = document.querySelectorAll('.menu-item');
    const toolPanels = document.querySelectorAll('.tool-panel');
    
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            const toolId = this.getAttribute('data-tool');
            
            // CLEAR ALL RESULTS when switching tools
            document.querySelectorAll('.results').forEach(div => {
                div.classList.add('hidden');
                div.innerHTML = '';
            });
            
            // Update menu
            menuItems.forEach(mi => mi.classList.remove('active'));
            this.classList.add('active');
            
            // Show tool panel
            toolPanels.forEach(panel => panel.classList.remove('active'));
            const targetPanel = document.getElementById(toolId);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });
    
    
    // ==========================================================================
    // FILE UPLOAD & HASH
    // ==========================================================================
    
    const fileUploadForm = document.getElementById('fileUploadForm');
    if (fileUploadForm) {
        fileUploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            const resultsDiv = document.getElementById('fileUploadResults');
            
            if (!file) {
                showError(resultsDiv, 'Please select a file');
                return;
            }
            
            showLoading(resultsDiv, 'Uploading and analyzing file...');
            
            try {
                const formData = new FormData();
                formData.append('file', file);
                // ✅ MODIFIED: Add investigation_id
                const investigationId = getCurrentInvestigationId();
                if (investigationId) {
                    formData.append('investigation_id', investigationId);
                }
                
                const response = await fetch('/upload-file', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    displayFileUploadResults(data, resultsDiv);
                } else {
                    showError(resultsDiv, data.error || 'Upload failed');
                }
            } catch (error) {
                showError(resultsDiv, 'Upload failed: ' + error.message);
            }
        });
    }
    
    
    // ==========================================================================
    // EXIFTOOL
    // ==========================================================================
    
    const exifForm = document.getElementById('exifForm');
    if (exifForm) {
        exifForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const fileInput = document.getElementById('exifFileInput');
            const file = fileInput.files[0];
            const resultsDiv = document.getElementById('exifResults');
            
            if (!file) {
                showError(resultsDiv, 'Please select a file');
                return;
            }
            
            showLoading(resultsDiv, 'Extracting metadata...');
            
            try {
                const formData = new FormData();
                formData.append('file', file);
                // ✅ MODIFIED: Add investigation_id
                const investigationId = getCurrentInvestigationId();
                if (investigationId) {
                    formData.append('investigation_id', investigationId);
                }
                
                const response = await fetch('/extract-exif', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    displayExifResults(data, resultsDiv);
                } else {
                    showError(resultsDiv, data.error || 'Extraction failed');
                }
            } catch (error) {
                showError(resultsDiv, 'Extraction failed: ' + error.message);
            }
        });
    }
    
    
    // ==========================================================================
    // GOOGLE DORKING
    // ==========================================================================
    
    const dorkForm = document.getElementById('dorkForm');
    if (dorkForm) {
        dorkForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const target = document.getElementById('dorkTarget').value.trim();
            const dork_type = document.getElementById('dorkType').value;
            const resultsDiv = document.getElementById('dorkResults');
            
            showLoading(resultsDiv, 'Generating dorks...');
            
            try {
                const data = await makeRequest('/google-dork', { target, dork_type });
                displayDorkResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    
    // ==========================================================================
    // REVERSE IP
    // ==========================================================================
    
    const reverseIpForm = document.getElementById('reverseIpForm');
    if (reverseIpForm) {
        reverseIpForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const ip = document.getElementById('reverseIpInput').value.trim();
            const resultsDiv = document.getElementById('reverseIpResults');
            
            showLoading(resultsDiv, 'Finding domains...');
            
            try {
                const data = await makeRequest('/reverse-ip', { ip });
                displayReverseIPResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    
    // ==========================================================================
    // EMAIL OSINT
    // ==========================================================================
    
    const emailOsintForm = document.getElementById('emailOsintForm');
    if (emailOsintForm) {
        emailOsintForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = document.getElementById('emailOsintInput').value.trim();
            const resultsDiv = document.getElementById('emailOsintResults');
            
            showLoading(resultsDiv, 'Investigating email...');
            
            try {
                const data = await makeRequest('/email-osint', { email });
                displayEmailOSINTResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    
    // ==========================================================================
    // WAYBACK MACHINE
    // ==========================================================================
    
    const waybackForm = document.getElementById('waybackForm');
    if (waybackForm) {
        waybackForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const url = document.getElementById('waybackInput').value.trim();
            const resultsDiv = document.getElementById('waybackResults');
            
            showLoading(resultsDiv, 'Checking archives...');
            
            try {
                const data = await makeRequest('/wayback-machine', { url });
                displayWaybackResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    
    // ==========================================================================
    // MAC LOOKUP
    // ==========================================================================
    
    const macForm = document.getElementById('macForm');
    if (macForm) {
        macForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const mac = document.getElementById('macInput').value.trim();
            const resultsDiv = document.getElementById('macResults');
            
            showLoading(resultsDiv, 'Looking up vendor...');
            
            try {
                const data = await makeRequest('/mac-lookup', { mac });
                displayMACResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    
    // ==========================================================================
    // CRYPTO TRACKER
    // ==========================================================================
    
    const cryptoForm = document.getElementById('cryptoForm');
    if (cryptoForm) {
        cryptoForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const address = document.getElementById('cryptoAddress').value.trim();
            const type = document.getElementById('cryptoType').value;
            const resultsDiv = document.getElementById('cryptoResults');
            
            showLoading(resultsDiv, 'Tracking address...');
            
            try {
                const data = await makeRequest('/crypto-tracker', { address, type });
                displayCryptoResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    
    // ==========================================================================
    // EXISTING TOOLS - UPDATED
    // ==========================================================================
    
    const hashForm = document.getElementById('hashForm');
    if (hashForm) {
        hashForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const hash = document.getElementById('hashInput').value.trim();
            const resultsDiv = document.getElementById('hashResults');
            
            showLoading(resultsDiv, 'Checking hash...');
            
            try {
                const data = await makeRequest('/check-hash', { hash });
                displayHashResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    const ipForm = document.getElementById('ipForm');
    if (ipForm) {
        ipForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const ip = document.getElementById('ipInput').value.trim();
            const resultsDiv = document.getElementById('ipResults');
            
            showLoading(resultsDiv, 'Checking IP...');
            
            try {
                const data = await makeRequest('/check-ip', { ip });
                displayIPResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    const geoForm = document.getElementById('geoForm');
    if (geoForm) {
        geoForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const ip = document.getElementById('geoInput').value.trim();
            const resultsDiv = document.getElementById('geoResults');
            
            showLoading(resultsDiv, 'Getting location...');
            
            try {
                const data = await makeRequest('/geolocate-ip', { ip });
                displayGeolocationResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    const whoisForm = document.getElementById('whoisForm');
    if (whoisForm) {
        whoisForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const domain = document.getElementById('whoisInput').value.trim();
            const resultsDiv = document.getElementById('whoisResults');
            
            showLoading(resultsDiv, 'Looking up domain...');
            
            try {
                const data = await makeRequest('/whois-lookup', { domain });
                displayWhoisResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    const breachForm = document.getElementById('emailForm');
    if (breachForm) {
        breachForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = document.getElementById('emailInput').value.trim();
            const resultsDiv = document.getElementById('emailResults');
            
            showLoading(resultsDiv, 'Checking breaches...');
            
            try {
                const data = await makeRequest('/email-breach', { email });
                displayEmailBreachResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    const usernameForm = document.getElementById('usernameForm');
    if (usernameForm) {
        usernameForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('usernameInput').value.trim();
            const resultsDiv = document.getElementById('usernameResults');
            
            showLoading(resultsDiv, 'Searching platforms...');
            
            try {
                const data = await makeRequest('/username-search', { username });
                displayUsernameResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    const subdomainForm = document.getElementById('subdomainForm');
    if (subdomainForm) {
        subdomainForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const domain = document.getElementById('subdomainInput').value.trim();
            const resultsDiv = document.getElementById('subdomainResults');
            
            showLoading(resultsDiv, 'Enumerating subdomains...');
            
            try {
                const data = await makeRequest('/subdomain-enum', { domain });
                displaySubdomainResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    const dnsForm = document.getElementById('dnsForm');
    if (dnsForm) {
        dnsForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const domain = document.getElementById('dnsInput').value.trim();
            const resultsDiv = document.getElementById('dnsResults');
            
            showLoading(resultsDiv, 'Looking up DNS records...');
            
            try {
                const data = await makeRequest('/dns-lookup', { domain });
                displayDNSResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    const sslForm = document.getElementById('sslForm');
    if (sslForm) {
        sslForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const domain = document.getElementById('sslInput').value.trim();
            const resultsDiv = document.getElementById('sslResults');
            
            showLoading(resultsDiv, 'Checking SSL certificate...');
            
            try {
                const data = await makeRequest('/ssl-info', { domain });
                displaySSLResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    const phoneForm = document.getElementById('phoneForm');
    if (phoneForm) {
        phoneForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const phone = document.getElementById('phoneInput').value.trim();
            const resultsDiv = document.getElementById('phoneResults');
            
            showLoading(resultsDiv, 'Looking up phone number...');
            
            try {
                const data = await makeRequest('/phone-lookup', { phone });
                displayPhoneResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    const shodanForm = document.getElementById('shodanForm');
    if (shodanForm) {
        shodanForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const query = document.getElementById('shodanQuery').value.trim();
            const resultsDiv = document.getElementById('shodanResults');
            
            showLoading(resultsDiv, 'Searching Shodan...');
            
            try {
                const data = await makeRequest('/shodan-search', { query });
                displayShodanResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    
    // ==========================================================================
    // DISPLAY FUNCTIONS - NEW TOOLS
    // ==========================================================================
    
    function displayFileUploadResults(data, container) {
        let html = '<h3>File Analysis</h3>';
        html += `<div class="result-item"><span class="result-label">File:</span><span class="result-value">${data.filename}</span></div>`;
        html += `<div class="result-item"><span class="result-label">Size:</span><span class="result-value">${formatBytes(data.size)}</span></div>`;
        html += `<div class="result-item"><span class="result-label">MD5:</span><span class="result-value"><code>${data.md5}</code></span></div>`;
        html += `<div class="result-item"><span class="result-label">SHA256:</span><span class="result-value"><code>${data.sha256}</code></span></div>`;
        
        if (data.virustotal && data.virustotal.found) {
            const badge = data.virustotal.is_malicious ? '<span class="badge badge-danger">⚠️ Malicious</span>' : '<span class="badge badge-safe">✓ Clean</span>';
            html += `<div class="result-item"><span class="result-label">VirusTotal:</span>${badge}</div>`;
            html += `<div class="result-item"><span class="result-label">Detections:</span><span class="result-value">${data.virustotal.detections} / ${data.virustotal.total_scanners}</span></div>`;
        }
        
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayExifResults(data, container) {
        let html = '<h3>Metadata Extraction</h3>';
        html += `<div class="result-item"><span class="result-label">File:</span><span class="result-value">${data.filename}</span></div>`;
        
        if (data.metadata) {
            html += '<div class="metadata-grid">';
            for (const [key, value] of Object.entries(data.metadata)) {
                if (key !== 'SourceFile') {
                    html += `<div class="metadata-item"><span class="meta-key">${key}:</span><span class="meta-value">${value}</span></div>`;
                }
            }
            html += '</div>';
        }
        
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayDorkResults(data, container) {
        let html = '<h3>Google Dorks</h3>';
        html += `<div class="result-item"><span class="result-label">Target:</span><span class="result-value">${data.target}</span></div>`;
        html += `<div class="result-item"><span class="result-label">Type:</span><span class="result-value">${data.dork_type}</span></div>`;
        
        if (data.dorks && data.dorks.length) {
            html += '<div class="dork-list">';
            data.dorks.forEach(dork => {
                const encoded = encodeURIComponent(dork);
                html += `<div class="dork-item"><code>${dork}</code><a href="${data.google_url_base}${encoded}" target="_blank" class="dork-link">Search →</a></div>`;
            });
            html += '</div>';
        }
        
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayReverseIPResults(data, container) {
        let html = '<h3>Reverse IP</h3>';
        html += `<div class="result-item"><span class="result-label">IP:</span><span class="result-value">${data.ip}</span></div>`;
        html += `<div class="result-item"><span class="result-label">Domains Found:</span><span class="result-value">${data.domains_found}</span></div>`;
        
        if (data.domains && data.domains.length > 0) {
            html += '<div class="domain-list">';
            data.domains.forEach(d => html += `<div class="domain-item">${d}</div>`);
            html += '</div>';
        }
        
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayEmailOSINTResults(data, container) {
        let html = '<h3>Email OSINT</h3>';
        html += `<div class="result-item"><span class="result-label">Email:</span><span class="result-value">${data.email}</span></div>`;
        html += `<div class="result-item"><span class="result-label">Valid:</span><span class="result-value">${data.valid_format ? '✓' : '✗'}</span></div>`;
        if (data.domain) {
            html += `<div class="result-item"><span class="result-label">Domain:</span><span class="result-value">${data.domain}</span></div>`;
            html += `<div class="result-item"><span class="result-label">Mail Server:</span><span class="result-value">${data.email_server_exists ? '✓ Exists' : '✗ Not found'}</span></div>`;
        }
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayWaybackResults(data, container) {
        let html = '<h3>Wayback Machine</h3>';
        if (data.archived) {
            html += `<div class="result-item"><span class="result-label">Status:</span><span class="result-value"><span class="badge badge-safe">✓ Archived</span></span></div>`;
            html += `<div class="snapshot-preview"><p>Snapshot available!</p><a href="${data.snapshot_url}" target="_blank" class="snapshot-link">View →</a></div>`;
        } else {
            html += `<div class="result-item"><span class="result-label">Status:</span><span class="result-value"><span class="badge badge-warning">Not Archived</span></span></div>`;
        }
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayMACResults(data, container) {
        let html = '<h3>MAC Lookup</h3>';
        html += `<div class="result-item"><span class="result-label">MAC:</span><span class="result-value">${data.mac}</span></div>`;
        html += `<div class="result-item"><span class="result-label">Vendor:</span><span class="result-value">${data.vendor}</span></div>`;
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayCryptoResults(data, container) {
        let html = '<h3>Crypto Tracker</h3>';
        if (data.demo_mode) html += `<div class="demo-message">${data.message}</div>`;
        html += `<div class="result-item"><span class="result-label">Address:</span><span class="result-value">${data.address}</span></div>`;
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayIPResults(data, container) {
        let html = '<h3>IP Reputation</h3>';
        html += `<div class="result-item"><span class="result-label">IP:</span><span class="result-value">${data.ip}</span></div>`;
        
        if (data.abuseipdb) {
            const badge = data.abuseipdb.is_malicious ? '<span class="badge badge-danger">⚠️ Malicious</span>' : '<span class="badge badge-safe">✓ Clean</span>';
            html += `<div class="result-item"><span class="result-label">AbuseIPDB:</span>${badge}</div>`;
            html += `<div class="result-item"><span class="result-label">Abuse Score:</span><span class="result-value">${data.abuseipdb.abuse_score}%</span></div>`;
        }
        
        if (data.virustotal && data.virustotal.detections !== undefined) {
            html += `<div class="result-item"><span class="result-label">VirusTotal:</span><span class="result-value">${data.virustotal.detections} detections</span></div>`;
        }
        
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayPhoneResults(data, container) {
        let html = '<h3>Phone Lookup</h3>';
        if (data.demo_mode) html += `<div class="demo-message">${data.message}</div>`;
        html += `<div class="result-item"><span class="result-label">Phone:</span><span class="result-value">${data.phone}</span></div>`;
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayShodanResults(data, container) {
        let html = '<h3>Shodan Search</h3>';
        if (data.demo_mode) html += `<div class="demo-message">${data.message}</div>`;
        html += `<div class="result-item"><span class="result-label">Query:</span><span class="result-value">${data.query}</span></div>`;
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    
    // ==========================================================================
    // DISPLAY FUNCTIONS - EXISTING TOOLS (simplified)
    // ==========================================================================
    
    function displayHashResults(data, container) {
        let html = '<h3>Hash Check</h3>';
        if (data.found === false) {
            html += `<div class="info-box">${data.message}</div>`;
        } else {
            const badge = data.is_malicious ? '<span class="badge badge-danger">⚠️ Malicious</span>' : '<span class="badge badge-safe">✓ Clean</span>';
            html += `<div class="result-item"><span class="result-label">Status:</span>${badge}</div>`;
            html += `<div class="result-item"><span class="result-label">Detections:</span>${data.detections} / ${data.total_scanners}</div>`;
        }
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayGeolocationResults(data, container) {
        let html = '<h3>Geolocation</h3>';
        html += `<div class="result-item"><span class="result-label">IP:</span>${data.ip}</div>`;
        html += `<div class="result-item"><span class="result-label">Country:</span>${data.country}</div>`;
        html += `<div class="result-item"><span class="result-label">City:</span>${data.city}</div>`;
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayWhoisResults(data, container) {
        let html = '<h3>WHOIS</h3>';
        if (data.error) {
            html += `<div class="error-message">${data.error}</div>`;
        } else {
            html += `<div class="result-item"><span class="result-label">Domain:</span>${data.domain}</div>`;
            html += `<div class="result-item"><span class="result-label">Registrar:</span>${data.registrar}</div>`;
        }
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayEmailBreachResults(data, container) {
        let html = '<h3>Breach Check</h3>';
        const badge = data.breached ? '<span class="badge badge-danger">⚠️ Breached</span>' : '<span class="badge badge-safe">✓ Clean</span>';
        html += `<div class="result-item"><span class="result-label">Status:</span>${badge}</div>`;
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayUsernameResults(data, container) {
        let html = '<h3>Username Search</h3>';
        html += '<div class="platform-grid">';
        data.results.forEach(r => {
            const cls = r.exists ? 'found' : 'not-found';
            if (r.exists) {
                html += `<a href="${r.url}" target="_blank" class="platform-item ${cls}"><strong>${r.platform}</strong><br><span class="status">✓ Profile Found</span></a>`;
            } else {
                html += `<div class="platform-item ${cls}"><strong>${r.platform}</strong><br><span class="status">✗ Not Found</span></div>`;
            }
        });
        html += '</div>';
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displaySubdomainResults(data, container) {
        let html = '<h3>Subdomains</h3>';
        html += `<div class="result-item"><span class="result-label">Found:</span>${data.subdomains.length}</div>`;
        if (data.subdomains.length) {
            html += '<div class="subdomain-list">';
            data.subdomains.forEach(s => html += `<div class="subdomain-item">${s.subdomain}</div>`);
            html += '</div>';
        }
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayDNSResults(data, container) {
        let html = '<h3>DNS Records</h3>';
        for (const [type, records] of Object.entries(data.records)) {
            if (records && records.length) {
                html += `<div class="dns-record"><div class="dns-record-type">${type}</div>`;
                records.forEach(r => html += `<div class="dns-record-value">${r}</div>`);
                html += '</div>';
            }
        }
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displaySSLResults(data, container) {
        let html = '<h3>SSL Certificate</h3>';
        if (data.error) {
            html += `<div class="error-message">${data.error}</div>`;
        } else {
            const badge = data.valid ? '<span class="badge badge-safe">✓ Valid</span>' : '<span class="badge badge-danger">⚠️ Invalid</span>';
            html += `<div class="result-item"><span class="result-label">Status:</span>${badge}</div>`;
        }
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    
    // ==========================================================================
    // UTILITY FUNCTIONS
    // ✅ MODIFIED: makeRequest now includes investigation_id automatically
    // ==========================================================================
    
    async function makeRequest(endpoint, data) {
        // ✅ MODIFIED: Automatically add investigation_id to all requests
        const requestData = {
            ...data,
            investigation_id: getCurrentInvestigationId()
        };
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || 'Request failed');
        return result;
    }
    
    function showLoading(container, message) {
        container.innerHTML = `<div class="loading"></div> ${message}`;
        container.classList.remove('hidden');
    }
    
    function showError(container, message) {
        container.innerHTML = `<div class="error-message"><strong>Error:</strong> ${message}</div>`;
        container.classList.remove('hidden');
    }
    
    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
});
