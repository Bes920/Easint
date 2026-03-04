/**
 * OSINT A-Grade Platform - Complete JavaScript
 * All 18 tools with proper handlers
 */

document.addEventListener('DOMContentLoaded', function() {
    
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
            
            showLoading(resultsDiv, 'Looking up MAC...');
            
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
            const address = document.getElementById('cryptoInput').value.trim();
            const type = document.getElementById('cryptoType').value;
            const resultsDiv = document.getElementById('cryptoResults');
            
            showLoading(resultsDiv, 'Tracking wallet...');
            
            try {
                const data = await makeRequest('/crypto-tracker', { address, type });
                displayCryptoResults(data, resultsDiv);
            } catch (error) {
                showError(resultsDiv, error.message);
            }
        });
    }
    
    
    // ==========================================================================
    // EXISTING TOOLS
    // ==========================================================================
    
    // IP Checker (Enhanced with dual source)
    document.getElementById('ipForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        const ip = document.getElementById('ipInput').value.trim();
        const resultsDiv = document.getElementById('ipResults');
        showLoading(resultsDiv, 'Checking IP...');
        try {
            const data = await makeRequest('/check-ip', { ip });
            displayDualIPResults(data, resultsDiv);
        } catch (error) {
            showError(resultsDiv, error.message);
        }
    });
    
    // Hash Checker
    document.getElementById('hashForm')?.addEventListener('submit', async function(e) {
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
    
    // Geolocation
    document.getElementById('geoForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        const ip = document.getElementById('geoInput').value.trim();
        const resultsDiv = document.getElementById('geoResults');
        showLoading(resultsDiv, 'Geolocating...');
        try {
            const data = await makeRequest('/geolocate-ip', { ip });
            displayGeolocationResults(data, resultsDiv);
        } catch (error) {
            showError(resultsDiv, error.message);
        }
    });
    
    // WHOIS
    document.getElementById('whoisForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        const domain = document.getElementById('whoisInput').value.trim();
        const resultsDiv = document.getElementById('whoisResults');
        showLoading(resultsDiv, 'Looking up WHOIS...');
        try {
            const data = await makeRequest('/whois-lookup', { domain });
            displayWhoisResults(data, resultsDiv);
        } catch (error) {
            showError(resultsDiv, error.message);
        }
    });
    
    // Email Breach
    document.getElementById('emailForm')?.addEventListener('submit', async function(e) {
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
    
    // Username Search
    document.getElementById('usernameForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        const username = document.getElementById('usernameInput').value.trim();
        const resultsDiv = document.getElementById('usernameResults');
        showLoading(resultsDiv, 'Searching username...');
        try {
            const data = await makeRequest('/username-search', { username });
            displayUsernameResults(data, resultsDiv);
        } catch (error) {
            showError(resultsDiv, error.message);
        }
    });
    
    // Subdomains
    document.getElementById('subdomainForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        const domain = document.getElementById('subdomainInput').value.trim();
        const resultsDiv = document.getElementById('subdomainResults');
        showLoading(resultsDiv, 'Finding subdomains...');
        try {
            const data = await makeRequest('/subdomain-enum', { domain });
            displaySubdomainResults(data, resultsDiv);
        } catch (error) {
            showError(resultsDiv, error.message);
        }
    });
    
    // DNS
    document.getElementById('dnsForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        const domain = document.getElementById('dnsInput').value.trim();
        const resultsDiv = document.getElementById('dnsResults');
        showLoading(resultsDiv, 'Looking up DNS...');
        try {
            const data = await makeRequest('/dns-lookup', { domain });
            displayDNSResults(data, resultsDiv);
        } catch (error) {
            showError(resultsDiv, error.message);
        }
    });
    
    // SSL
    document.getElementById('sslForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        const domain = document.getElementById('sslInput').value.trim();
        const resultsDiv = document.getElementById('sslResults');
        showLoading(resultsDiv, 'Checking SSL...');
        try {
            const data = await makeRequest('/ssl-info', { domain });
            displaySSLResults(data, resultsDiv);
        } catch (error) {
            showError(resultsDiv, error.message);
        }
    });
    
    
    // ==========================================================================
    // DISPLAY FUNCTIONS - NEW TOOLS
    // ==========================================================================
    
    function displayFileUploadResults(data, container) {
        let html = '<h3>File Analysis</h3>';
        html += `<div class="result-item"><span class="result-label">File:</span><span class="result-value">${data.filename}</span></div>`;
        html += `<div class="result-item"><span class="result-label">Size:</span><span class="result-value">${formatBytes(data.size)}</span></div>`;
        html += `<div class="hash-display"><div class="hash-label">MD5:</div><div class="hash-value">${data.md5}</div></div>`;
        html += `<div class="hash-display"><div class="hash-label">SHA-256:</div><div class="hash-value">${data.sha256}</div></div>`;
        
        if (data.virustotal && data.virustotal.found) {
            const badge = data.virustotal.is_malicious ? 
                '<span class="badge badge-danger">⚠️ Malicious</span>' : 
                '<span class="badge badge-safe">✓ Clean</span>';
            html += `<h4 style="color: #00d9ff; margin-top: 20px;">VirusTotal:</h4>`;
            html += `<div class="result-item"><span class="result-label">Status:</span><span class="result-value">${badge}</span></div>`;
            html += `<div class="result-item"><span class="result-label">Detections:</span><span class="result-value">${data.virustotal.detections} / ${data.virustotal.total_scanners}</span></div>`;
        }
        
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayExifResults(data, container) {
        let html = '<h3>Metadata</h3>';
        html += `<div class="result-item"><span class="result-label">File:</span><span class="result-value">${data.filename}</span></div>`;
        
        if (data.metadata && Object.keys(data.metadata).length > 0) {
            html += '<div class="metadata-grid">';
            for (const [key, value] of Object.entries(data.metadata)) {
                html += `<div class="metadata-item"><div class="metadata-key">${key}</div><div class="metadata-value">${value}</div></div>`;
            }
            html += '</div>';
        } else {
            html += '<div class="info-box">No metadata found. Install ExifTool for full extraction.</div>';
        }
        
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayDualIPResults(data, container) {
        let html = '<h3>IP Reputation (Multi-Source)</h3>';
        html += `<div class="result-item"><span class="result-label">IP:</span><span class="result-value">${data.ip}</span></div>`;
        
        html += '<div class="dual-results">';
        
        // AbuseIPDB
        html += '<div class="result-source"><h4>AbuseIPDB</h4>';
        if (data.abuseipdb) {
            const badge = data.abuseipdb.is_malicious ? 
                '<span class="badge badge-danger">⚠️ Malicious</span>' : 
                '<span class="badge badge-safe">✓ Clean</span>';
            html += `<div class="result-item"><span class="result-label">Status:</span>${badge}</div>`;
            html += `<div class="result-item"><span class="result-label">Score:</span>${data.abuseipdb.abuse_score}%</div>`;
        }
        html += '</div>';
        
        // VirusTotal
        html += '<div class="result-source"><h4>VirusTotal</h4>';
        if (data.virustotal && !data.virustotal.error) {
            const badge = data.virustotal.is_malicious ? 
                '<span class="badge badge-danger">⚠️ Malicious</span>' : 
                '<span class="badge badge-safe">✓ Clean</span>';
            html += `<div class="result-item"><span class="result-label">Status:</span>${badge}</div>`;
            html += `<div class="result-item"><span class="result-label">Detections:</span>${data.virustotal.detections}</div>`;
        }
        html += '</div></div>';
        
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayDorkResults(data, container) {
        let html = '<h3>Google Dorks</h3>';
        html += `<div class="result-item"><span class="result-label">Target:</span><span class="result-value">${data.target}</span></div>`;
        html += `<div class="result-item"><span class="result-label">Category:</span><span class="result-value">${data.dork_type}</span></div>`;
        
        html += '<div class="dork-list">';
        data.dorks.forEach(dork => {
            const url = data.google_url_base + encodeURIComponent(dork);
            html += `<div class="dork-item"><div class="dork-query">${dork}</div><a href="${url}" target="_blank" class="dork-link">Search</a></div>`;
        });
        html += '</div>';
        
        container.innerHTML = html;
        container.classList.remove('hidden');
    }
    
    function displayReverseIPResults(data, container) {
        let html = '<h3>Reverse IP</h3>';
        html += `<div class="result-item"><span class="result-label">IP:</span><span class="result-value">${data.ip}</span></div>`;
        html += `<div class="result-item"><span class="result-label">Domains:</span><span class="result-value">${data.domains_found}</span></div>`;
        
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
            html += `<div class="platform-item ${cls}"><strong>${r.platform}</strong><br>${r.exists ? '✓' : '✗'}</div>`;
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
    // ==========================================================================
    
    async function makeRequest(endpoint, data) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
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
