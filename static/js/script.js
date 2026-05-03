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
    const toolDescriptionTitle = document.getElementById('toolDescriptionTitle');
    const toolDescriptionText = document.getElementById('toolDescriptionText');

    function updateToolDescription(button) {
        if (!button || !toolDescriptionTitle || !toolDescriptionText) return;
        const title = button.dataset.toolTitle || button.textContent.trim();
        const description = button.dataset.description || 'Select a tool to read a quick summary of what it can do.';
        toolDescriptionTitle.textContent = title;
        toolDescriptionText.textContent = description;
    }

    function activateTool(toolId) {
        const targetButton = document.querySelector(`.menu-item[data-tool="${toolId}"]`);
        if (!targetButton) return false;

        // Clear all results when switching tools
        document.querySelectorAll('.results').forEach(div => {
            div.classList.add('hidden');
            div.innerHTML = '';
        });

        menuItems.forEach(mi => mi.classList.remove('active'));
        targetButton.classList.add('active');

        toolPanels.forEach(panel => panel.classList.remove('active'));
        const targetPanel = document.getElementById(toolId);
        if (targetPanel) {
            targetPanel.classList.add('active');
        }

        updateToolDescription(targetButton);
        return true;
    }

    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            const toolId = this.getAttribute('data-tool');
            activateTool(toolId);
        });
    });

    const initialTool = document.querySelector('.menu-item.active');
    if (initialTool) {
        updateToolDescription(initialTool);
    }

    const toolFromQuery = new URLSearchParams(window.location.search).get('tool');
    const toolFromHash = window.location.hash ? window.location.hash.slice(1) : '';
    if (toolFromQuery) {
        activateTool(toolFromQuery);
    } else if (toolFromHash) {
        activateTool(toolFromHash);
    }
    
    
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
        html += renderResultItem('File', escapeHtml(data.filename || 'Unknown file'));
        html += renderResultItem('Size', escapeHtml(formatBytes(data.size || 0)));
        html += renderResultItem('MD5', renderCopyableValue(data.md5));
        html += renderResultItem('SHA256', renderCopyableValue(data.sha256));

        if (data.virustotal && data.virustotal.found) {
            const badge = data.virustotal.is_malicious ? '<span class="badge badge-danger">Malicious</span>' : '<span class="badge badge-safe">Clean</span>';
            html += renderResultItem('VirusTotal', badge);
            html += renderResultItem('Detections', escapeHtml(`${data.virustotal.detections} / ${data.virustotal.total_scanners}`));
        }

        renderResult(container, html, {
            toast: { type: 'success', title: 'File analyzed', message: `${data.filename || 'File'} is ready for review.` }
        });
    }

    function displayExifResults(data, container) {
        let html = '<h3>Metadata Extraction</h3>';
        html += renderResultItem('File', escapeHtml(data.filename || 'Uploaded file'));

        if (data.metadata) {
            html += '<div class="metadata-grid">';
            for (const [key, value] of Object.entries(data.metadata)) {
                if (key !== 'SourceFile') {
                    html += `<div class="metadata-item"><span class="metadata-key">${escapeHtml(key)}</span><span class="metadata-value">${escapeHtml(String(value))}</span></div>`;
                }
            }
            html += '</div>';
        }

        renderResult(container, html, {
            toast: { type: 'success', title: 'Metadata extracted', message: 'File metadata has been loaded below.' }
        });
    }

    function displayDorkResults(data, container) {
        let html = '<h3>Google Dorks</h3>';
        html += renderResultItem('Target', escapeHtml(data.target));
        html += renderResultItem('Type', escapeHtml(data.dork_type));

        if (data.dorks && data.dorks.length) {
            html += '<div class="dork-list">';
            data.dorks.forEach((dork) => {
                const encoded = encodeURIComponent(dork);
                html += `<div class="dork-item"><div class="result-stack"><code class="dork-query">${escapeHtml(dork)}</code></div><div class="result-actions">${renderCopyButton(dork, 'Copy dork')}<a href="${escapeAttribute((data.google_url_base || '') + encoded)}" target="_blank" rel="noopener noreferrer" class="dork-link">Search</a></div></div>`;
            });
            html += '</div>';
        }

        renderResult(container, html, {
            toast: { type: 'success', title: 'Dorks generated', message: `${(data.dorks || []).length} query suggestions are ready.` }
        });
    }

    function displayReverseIPResults(data, container) {
        let html = '<h3>Reverse IP</h3>';
        html += renderResultItem('IP', renderCopyableValue(data.ip));
        html += renderResultItem('Domains Found', escapeHtml(String(data.domains_found || 0)));

        if (data.domains && data.domains.length > 0) {
            html += '<div class="domain-list">';
            data.domains.forEach((domain) => {
                html += `<div class="domain-item">${escapeHtml(domain)} ${renderCopyButton(domain, 'Copy')}</div>`;
            });
            html += '</div>';
        }

        renderResult(container, html, {
            toast: { type: 'success', title: 'Reverse IP complete', message: `${data.domains_found || 0} domains were found.` }
        });
    }

    function displayEmailOSINTResults(data, container) {
        let html = '<h3>Email OSINT</h3>';
        html += renderResultItem('Email', renderCopyableValue(data.email));
        html += renderResultItem('Format Check', escapeHtml(data.valid_format ? 'Valid format' : 'Invalid format'));

        if (data.domain) {
            html += renderResultItem('Domain', renderCopyableValue(data.domain));
            html += renderResultItem('Mail Server', escapeHtml(data.email_server_exists ? 'Mail server detected' : 'No mail server found'));
        }

        renderResult(container, html, {
            toast: { type: 'success', title: 'Email analysis ready', message: `Finished checking ${data.email || 'the supplied address'}.` }
        });
    }

    function displayWaybackResults(data, container) {
        let html = '<h3>Wayback Machine</h3>';
        if (data.archived) {
            html += renderResultItem('Status', '<span class="badge badge-safe">Archived</span>');
            html += `<div class="snapshot-preview"><p>Snapshot available for review.</p><div class="result-actions"><a href="${escapeAttribute(data.snapshot_url || '#')}" target="_blank" rel="noopener noreferrer" class="snapshot-link dork-link">Open Snapshot</a>${renderCopyButton(data.snapshot_url || '', 'Copy link')}</div></div>`;
        } else {
            html += renderResultItem('Status', '<span class="badge badge-warning">No archive found</span>');
        }

        renderResult(container, html, {
            toast: { type: 'success', title: 'Archive check complete', message: data.archived ? 'A historical snapshot was found.' : 'No historical snapshot was found.' }
        });
    }

    function displayMACResults(data, container) {
        const html = [
            '<h3>MAC Lookup</h3>',
            renderResultItem('MAC', renderCopyableValue(data.mac)),
            renderResultItem('Vendor', escapeHtml(data.vendor || 'Unknown vendor'))
        ].join('');

        renderResult(container, html, {
            toast: { type: 'success', title: 'MAC lookup complete', message: 'Vendor details have been loaded.' }
        });
    }

    function displayCryptoResults(data, container) {
        let html = '<h3>Crypto Tracker</h3>';
        if (data.demo_mode) html += `<div class="demo-message">${escapeHtml(data.message || '')}</div>`;
        html += renderResultItem('Address', renderCopyableValue(data.address));

        renderResult(container, html, {
            toast: { type: 'success', title: 'Crypto lookup complete', message: 'Wallet information is now visible below.' }
        });
    }

    function displayIPResults(data, container) {
        let html = '<h3>IP Reputation</h3>';
        html += renderResultItem('IP', renderCopyableValue(data.ip));

        if (data.abuseipdb) {
            const badge = data.abuseipdb.is_malicious ? '<span class="badge badge-danger">Malicious</span>' : '<span class="badge badge-safe">Clean</span>';
            html += renderResultItem('AbuseIPDB', badge);
            html += renderResultItem('Abuse Score', escapeHtml(`${data.abuseipdb.abuse_score}%`));
        }

        if (data.virustotal && data.virustotal.detections !== undefined) {
            html += renderResultItem('VirusTotal', escapeHtml(`${data.virustotal.detections} detections`));
        }

        renderResult(container, html, {
            toast: { type: 'success', title: 'IP check complete', message: `Finished reviewing ${data.ip || 'the IP address'}.` }
        });
    }

    function displayPhoneResults(data, container) {
        let html = '<h3>Phone Lookup</h3>';
        if (data.demo_mode) html += `<div class="demo-message">${escapeHtml(data.message || '')}</div>`;
        html += renderResultItem('Phone', renderCopyableValue(data.phone));

        renderResult(container, html, {
            toast: { type: 'success', title: 'Phone lookup complete', message: 'The number check has finished.' }
        });
    }

    function displayShodanResults(data, container) {
        let html = '<h3>Shodan Search</h3>';
        if (data.demo_mode) html += `<div class="demo-message">${escapeHtml(data.message || '')}</div>`;
        html += renderResultItem('Query', renderCopyableValue(data.query));

        renderResult(container, html, {
            toast: { type: 'success', title: 'Shodan query complete', message: 'Search details were returned successfully.' }
        });
    }

    function displayHashResults(data, container) {
        let html = '<h3>Hash Check</h3>';
        if (data.found === false) {
            html += `<div class="info-box">${escapeHtml(data.message || 'No matching hash was found.')}</div>`;
        } else {
            const badge = data.is_malicious ? '<span class="badge badge-danger">Malicious</span>' : '<span class="badge badge-safe">Clean</span>';
            html += renderResultItem('Status', badge);
            html += renderResultItem('Detections', escapeHtml(`${data.detections} / ${data.total_scanners}`));
        }

        renderResult(container, html, {
            toast: { type: 'success', title: 'Hash lookup complete', message: 'Hash intelligence is ready below.' }
        });
    }

    function displayGeolocationResults(data, container) {
        const html = [
            '<h3>Geolocation</h3>',
            renderResultItem('IP', renderCopyableValue(data.ip)),
            renderResultItem('Country', escapeHtml(data.country || 'Unknown')),
            renderResultItem('City', escapeHtml(data.city || 'Unknown'))
        ].join('');

        renderResult(container, html, {
            toast: { type: 'success', title: 'Geolocation ready', message: 'Location details have been loaded.' }
        });
    }

    function displayWhoisResults(data, container) {
        if (data.error) {
            showError(container, data.error);
            return;
        }

        const html = [
            '<h3>WHOIS</h3>',
            renderResultItem('Domain', renderCopyableValue(data.domain)),
            renderResultItem('Registrar', escapeHtml(data.registrar || 'Unavailable'))
        ].join('');

        renderResult(container, html, {
            toast: { type: 'success', title: 'WHOIS complete', message: 'Domain registration details are available.' }
        });
    }

    function displayEmailBreachResults(data, container) {
        const badge = data.breached ? '<span class="badge badge-danger">Breached</span>' : '<span class="badge badge-safe">Clean</span>';
        const html = ['<h3>Breach Check</h3>', renderResultItem('Status', badge)].join('');

        renderResult(container, html, {
            toast: { type: 'success', title: 'Breach check complete', message: 'The breach status has been updated.' }
        });
    }

    function displayUsernameResults(data, container) {
        let html = '<h3>Username Search</h3><div class="platform-grid">';
        (data.results || []).forEach((result) => {
            const cls = result.exists ? 'found' : 'not-found';
            const platform = escapeHtml(result.platform || 'Platform');
            if (result.exists) {
                html += `<a href="${escapeAttribute(result.url || '#')}" target="_blank" rel="noopener noreferrer" class="platform-item ${cls}"><strong>${platform}</strong><br><span class="status">Profile Found</span></a>`;
            } else {
                html += `<div class="platform-item ${cls}"><strong>${platform}</strong><br><span class="status">Not Found</span></div>`;
            }
        });
        html += '</div>';

        renderResult(container, html, {
            toast: { type: 'success', title: 'Username scan complete', message: `${(data.results || []).length} platform checks finished.` }
        });
    }

    function displaySubdomainResults(data, container) {
        const subdomains = data.subdomains || [];
        let html = '<h3>Subdomains</h3>';
        html += renderResultItem('Found', escapeHtml(String(subdomains.length)));
        if (subdomains.length) {
            html += '<div class="subdomain-list">';
            subdomains.forEach((item) => {
                const subdomain = item.subdomain || item;
                html += `<div class="subdomain-item">${escapeHtml(subdomain)} ${renderCopyButton(subdomain, 'Copy')}</div>`;
            });
            html += '</div>';
        }

        renderResult(container, html, {
            toast: { type: 'success', title: 'Subdomain scan complete', message: `${subdomains.length} subdomains were identified.` }
        });
    }

    function displayDNSResults(data, container) {
        let html = '<h3>DNS Records</h3>';
        const records = data.records || {};
        for (const [type, entries] of Object.entries(records)) {
            if (entries && entries.length) {
                html += `<div class="dns-record"><div class="dns-record-type">${escapeHtml(type)}</div>`;
                entries.forEach((entry) => {
                    html += `<div class="dns-record-value">${escapeHtml(String(entry))} ${renderCopyButton(String(entry), 'Copy')}</div>`;
                });
                html += '</div>';
            }
        }

        renderResult(container, html, {
            toast: { type: 'success', title: 'DNS lookup complete', message: 'DNS record data is ready.' }
        });
    }

    function displaySSLResults(data, container) {
        if (data.error) {
            showError(container, data.error);
            return;
        }

        const badge = data.valid ? '<span class="badge badge-safe">Valid</span>' : '<span class="badge badge-danger">Invalid</span>';
        const html = ['<h3>SSL Certificate</h3>', renderResultItem('Status', badge)].join('');

        renderResult(container, html, {
            toast: { type: 'success', title: 'SSL lookup complete', message: 'Certificate status has been refreshed.' }
        });
    }

    async function makeRequest(endpoint, data) {
        const requestData = {
            ...data,
            investigation_id: getCurrentInvestigationId()
        };

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        const result = await parseJsonResponse(response);
        if (!response.ok) {
            throw new Error(normalizeErrorMessage(result.error || result.message || 'The request could not be completed.'));
        }

        return result;
    }

    async function parseJsonResponse(response) {
        try {
            return await response.json();
        } catch (error) {
            console.error('Failed to parse JSON response:', error);
            throw new Error('The server returned an unexpected response. Please try again.');
        }
    }

    function showLoading(container, message) {
        setFormBusy(container, true, message);
        container.innerHTML = `
            <div class="loading-state-panel">
                <div class="loading" aria-hidden="true"></div>
                <div class="loading-copy">
                    <span class="loading-label">${escapeHtml(message)}</span>
                    <span class="loading-subtext">This may take a few seconds depending on the source.</span>
                </div>
            </div>
        `;
        container.classList.remove('hidden');
    }

    function showError(container, message) {
        const normalized = normalizeErrorMessage(message);
        setFormBusy(container, false);
        container.innerHTML = `
            <div class="error-message">
                <strong class="error-title">Request could not be completed</strong>
                <div>${escapeHtml(normalized)}</div>
                <div class="error-help">Check the input format or try again in a moment.</div>
            </div>
        `;
        container.classList.remove('hidden');
        showToast('error', 'Request failed', normalized);
    }

    function renderResult(container, html, options = {}) {
        setFormBusy(container, false);
        container.innerHTML = html;
        container.classList.remove('hidden');

        if (options.toast) {
            showToast(options.toast.type || 'success', options.toast.title, options.toast.message);
        }
    }

    function renderResultItem(label, valueMarkup) {
        return `<div class="result-item"><span class="result-label">${escapeHtml(label)}</span><div class="result-actions">${valueMarkup}</div></div>`;
    }

    function renderCopyableValue(value) {
        if (!value) {
            return '<span class="result-value">Unavailable</span>';
        }

        return `<span class="result-value"><code class="result-copy-text">${escapeHtml(String(value))}</code></span>${renderCopyButton(String(value))}`;
    }

    function renderCopyButton(value, label = 'Copy') {
        if (!value) {
            return '';
        }

        return `<button type="button" class="btn-copy" data-copy-text="${escapeAttribute(String(value))}">${escapeHtml(label)}</button>`;
    }

    function ensureToastRegion() {
        let region = document.querySelector('.toast-region');
        if (!region) {
            region = document.createElement('div');
            region.className = 'toast-region';
            region.setAttribute('aria-live', 'polite');
            region.setAttribute('aria-atomic', 'true');
            document.body.appendChild(region);
        }
        return region;
    }

    function showToast(type, title, message) {
        const region = ensureToastRegion();
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `<strong class="toast-title">${escapeHtml(title)}</strong><div class="toast-message">${escapeHtml(message)}</div>`;
        region.appendChild(toast);

        window.setTimeout(() => {
            toast.remove();
        }, 3200);
    }

    function setFormBusy(container, isBusy, label = 'Working...') {
        const form = container.previousElementSibling;
        if (!form || !form.classList.contains('tool-form')) return;

        const button = form.querySelector('button[type="submit"]');
        if (!button) return;

        if (!button.dataset.defaultLabel) {
            button.dataset.defaultLabel = button.innerHTML;
        }

        button.disabled = isBusy;
        button.classList.toggle('is-loading', isBusy);
        button.setAttribute('aria-busy', isBusy ? 'true' : 'false');
        button.innerHTML = isBusy
            ? `<span class="btn-icon">⏳</span> ${escapeHtml(label)}`
            : button.dataset.defaultLabel;
    }

    function normalizeErrorMessage(message) {
        const trimmed = String(message || '').trim();
        if (!trimmed) return 'Something went wrong while talking to the server.';
        if (trimmed.toLowerCase().includes('failed to fetch')) {
            return 'The request could not reach the server. Check that the app is still running and try again.';
        }
        return trimmed;
    }

    document.addEventListener('click', async function(event) {
        const copyButton = event.target.closest('[data-copy-text]');
        if (!copyButton) return;

        const text = copyButton.getAttribute('data-copy-text') || '';
        try {
            await navigator.clipboard.writeText(text);
            const originalLabel = copyButton.textContent;
            copyButton.textContent = 'Copied';
            copyButton.classList.add('copied');
            showToast('success', 'Copied to clipboard', 'The selected value is ready to paste.');

            window.setTimeout(() => {
                copyButton.textContent = originalLabel;
                copyButton.classList.remove('copied');
            }, 1400);
        } catch (error) {
            console.error('Clipboard copy failed:', error);
            showToast('error', 'Copy failed', 'Your browser blocked clipboard access for this action.');
        }
    });

    function escapeHtml(value) {
        return String(value ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function escapeAttribute(value) {
        return escapeHtml(value).replace(/`/g, '&#96;');
    }

    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
});
