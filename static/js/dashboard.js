/**
 * EASINT - Investigation Dashboard
 * ✅ ALL BUGS FIXED:
 * 1. Search functionality working
 * 2. Filter dropdowns working
 * 3. "No results" logic fixed
 * 4. "No investigations" logic fixed
 */

// ==========================================================================
// THEME SWITCHER (Same as main page)
// ==========================================================================

(function initTheme() {
    const savedTheme = localStorage.getItem('easint-theme') || 'system';
    applyTheme(savedTheme);
    updateThemeIcon(savedTheme);
})();

function applyTheme(theme) {
    if (theme === 'system') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    } else {
        document.documentElement.setAttribute('data-theme', theme);
    }
}

function updateThemeIcon(theme) {
    const themeIcon = document.querySelector('.theme-icon');
    if (!themeIcon) return;
    
    if (theme === 'light') {
        themeIcon.textContent = '☀️';
    } else if (theme === 'dark') {
        themeIcon.textContent = '🌙';
    } else {
        themeIcon.textContent = '💻';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    const themeMenu = document.getElementById('themeMenu');
    const themeOptions = document.querySelectorAll('.theme-option');
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            themeMenu.classList.toggle('hidden');
        });
    }
    
    document.addEventListener('click', function(e) {
        if (themeMenu && !themeMenu.contains(e.target) && e.target !== themeToggle) {
            themeMenu.classList.add('hidden');
        }
    });
    
    themeOptions.forEach(option => {
        option.addEventListener('click', function() {
            const selectedTheme = this.getAttribute('data-theme');
            themeOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            applyTheme(selectedTheme);
            updateThemeIcon(selectedTheme);
            localStorage.setItem('easint-theme', selectedTheme);
            themeMenu.classList.add('hidden');
        });
    });
});

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
    const savedTheme = localStorage.getItem('easint-theme');
    if (savedTheme === 'system' || !savedTheme) {
        applyTheme('system');
    }
});


// ==========================================================================
// DASHBOARD STATE
// ==========================================================================

let investigations = [];
let filteredInvestigations = [];
let currentInvestigation = null;

// ==========================================================================
// INITIALIZE DASHBOARD
// ==========================================================================

document.addEventListener('DOMContentLoaded', function() {
    loadInvestigations();
    setupEventListeners();
});

function setupEventListeners() {
    // Create investigation button
    document.getElementById('createInvestigationBtn').addEventListener('click', openCreateModal);
    
    // Create investigation form
    document.getElementById('createInvestigationForm').addEventListener('submit', createInvestigation);
    
    // ✅ FIX: Search and filters now working
    document.getElementById('searchInput').addEventListener('input', filterInvestigations);
    document.getElementById('statusFilter').addEventListener('change', filterInvestigations);
    document.getElementById('sortFilter').addEventListener('change', filterInvestigations);
}

// ==========================================================================
// LOAD INVESTIGATIONS
// ==========================================================================

async function loadInvestigations() {
    try {
        const response = await fetch('/api/investigations');
        const data = await response.json();
        
        investigations = data.investigations || [];
        filteredInvestigations = [...investigations]; // ✅ FIX: Initialize filtered list
        renderInvestigations(filteredInvestigations);
        updateStats(investigations);
        
    } catch (error) {
        console.error('Error loading investigations:', error);
        showError('Failed to load investigations');
    }
}

// ==========================================================================
// RENDER INVESTIGATIONS
// ==========================================================================

function renderInvestigations(investigationsToRender) {
    const grid = document.getElementById('investigationsGrid');
    const loading = document.getElementById('loadingState');
    const empty = document.getElementById('emptyState');
    
    // ✅ FIX: Hide loading state
    if (loading) {
        loading.style.display = 'none';
    }
    
    // ✅ FIX: Only show empty state if NO investigations exist at all
    if (investigations.length === 0) {
        grid.innerHTML = '';
        if (empty) {
            empty.classList.remove('hidden');
        }
        return;
    }
    
    // ✅ FIX: Hide empty state if we have investigations
    if (empty) {
        empty.classList.add('hidden');
    }
    
    // ✅ FIX: Show "no results" for filtered view, not empty state
    if (investigationsToRender.length === 0 && investigations.length > 0) {
        grid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px; color: var(--text-tertiary);">
                <div style="font-size: 3em; margin-bottom: 15px;">🔍</div>
                <h3 style="color: var(--text-primary); margin-bottom: 10px;">No matching investigations</h3>
                <p>Try adjusting your search or filters</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = investigationsToRender.map(inv => `
        <div class="investigation-card" onclick="viewInvestigation('${inv.id}')">
            <div class="card-header">
                <div>
                    <h3 class="card-title">${escapeHtml(inv.name)}</h3>
                </div>
                <span class="card-status status-${inv.status}">${inv.status}</span>
            </div>
            
            ${inv.description ? `<p class="card-description">${escapeHtml(inv.description)}</p>` : ''}
            
            <div class="card-meta">
                <div class="meta-item">
                    <span>📅</span>
                    <span>${formatDate(inv.created_at)}</span>
                </div>
                ${inv.tags && inv.tags.length > 0 ? `
                    <div class="meta-item">
                        <span>🏷️</span>
                        <span>${inv.tags.slice(0, 2).join(', ')}${inv.tags.length > 2 ? '...' : ''}</span>
                    </div>
                ` : ''}
            </div>
            
            <div class="card-stats">
                <div class="stat-item">
                    <span class="stat-icon-sm">📊</span>
                    <span class="stat-number">${inv.result_count || 0}</span>
                    <span>results</span>
                </div>
                ${inv.threat_level ? `
                    <div class="stat-item">
                        <span class="threat-badge threat-${inv.threat_level}">${getThreatIcon(inv.threat_level)} ${inv.threat_level.toUpperCase()}</span>
                    </div>
                ` : ''}
            </div>
        </div>
    `).join('');
}

// ==========================================================================
// UPDATE STATS
// ==========================================================================

function updateStats(investigationsData) {
    const total = investigationsData.length;
    const active = investigationsData.filter(inv => inv.status === 'active').length;
    const completed = investigationsData.filter(inv => inv.status === 'completed').length;
    
    // Count high threat results
    let highThreat = 0;
    investigationsData.forEach(inv => {
        if (inv.threat_level === 'high' || inv.threat_level === 'critical') {
            highThreat++;
        }
    });
    
    document.getElementById('totalInvestigations').textContent = total;
    document.getElementById('activeInvestigations').textContent = active;
    document.getElementById('completedInvestigations').textContent = completed;
    document.getElementById('highThreatCount').textContent = highThreat;
}

// ==========================================================================
// FILTER INVESTIGATIONS (✅ NOW WORKING!)
// ==========================================================================

function filterInvestigations() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;
    const sortFilter = document.getElementById('sortFilter').value;
    
    // ✅ FIX: Filter logic
    filteredInvestigations = investigations.filter(inv => {
        // Search filter
        const matchesSearch = !searchTerm || 
            inv.name.toLowerCase().includes(searchTerm) ||
            (inv.description && inv.description.toLowerCase().includes(searchTerm)) ||
            (inv.tags && inv.tags.some(tag => tag.toLowerCase().includes(searchTerm)));
        
        // Status filter
        const matchesStatus = statusFilter === 'all' || inv.status === statusFilter;
        
        return matchesSearch && matchesStatus;
    });
    
    // ✅ FIX: Sort logic
    filteredInvestigations.sort((a, b) => {
        switch (sortFilter) {
            case 'newest':
                return new Date(b.created_at) - new Date(a.created_at);
            case 'oldest':
                return new Date(a.created_at) - new Date(b.created_at);
            case 'most-results':
                return (b.result_count || 0) - (a.result_count || 0);
            case 'highest-threat':
                const threatOrder = { critical: 4, high: 3, medium: 2, low: 1, safe: 0 };
                return (threatOrder[b.threat_level] || 0) - (threatOrder[a.threat_level] || 0);
            default:
                return 0;
        }
    });
    
    renderInvestigations(filteredInvestigations);
}

// ==========================================================================
// CREATE INVESTIGATION MODAL
// ==========================================================================

function openCreateModal() {
    document.getElementById('createInvestigationModal').classList.remove('hidden');
    // Clear form
    document.getElementById('investigationName').value = '';
    document.getElementById('investigationDescription').value = '';
    document.getElementById('investigationTags').value = '';
}

function closeCreateModal() {
    document.getElementById('createInvestigationModal').classList.add('hidden');
}

// ==========================================================================
// CREATE INVESTIGATION
// ==========================================================================

async function createInvestigation(e) {
    e.preventDefault();
    
    const name = document.getElementById('investigationName').value.trim();
    const description = document.getElementById('investigationDescription').value.trim();
    const tagsInput = document.getElementById('investigationTags').value.trim();
    const tags = tagsInput ? tagsInput.split(',').map(t => t.trim()).filter(t => t) : [];
    
    if (!name) {
        showError('Please enter an investigation name');
        return;
    }
    
    try {
        const response = await fetch('/api/investigations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description, tags })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            closeCreateModal();
            showSuccess('Investigation created successfully!');
            loadInvestigations(); // Reload to show new investigation
        } else {
            showError(data.error || 'Failed to create investigation');
        }
    } catch (error) {
        console.error('Error creating investigation:', error);
        showError('Failed to create investigation');
    }
}

// ==========================================================================
// VIEW INVESTIGATION DETAILS
// ==========================================================================

async function viewInvestigation(investigationId) {
    try {
        const response = await fetch(`/api/investigations/${investigationId}`);
        const data = await response.json();
        
        if (response.ok) {
            const investigation = data.investigation || data;
            investigation.aiSummary = investigation.ai_summary || null;
            investigation.aiAnalyzedAt = investigation.ai_analyzed_at || null;
            currentInvestigation = investigation;
            showInvestigationDetails(investigation);
        } else {
            showError('Failed to load investigation details');
        }
    } catch (error) {
        console.error('Error loading investigation:', error);
        showError('Failed to load investigation details');
    }
}

function showInvestigationDetails(investigation) {
    resetAnalysisSection();

    // Set basic info
    document.getElementById('detailsInvestigationName').textContent = investigation.name;
    document.getElementById('detailsInvestigationMeta').textContent = 
        `Created: ${formatDate(investigation.created_at)} | Updated: ${formatDate(investigation.updated_at)}`;
    document.getElementById('detailsStatus').value = investigation.status;
    document.getElementById('detailsDescription').textContent = investigation.description || '—';
    
    // Set tags
    const tagsContainer = document.getElementById('detailsTags');
    if (investigation.tags && investigation.tags.length > 0) {
        tagsContainer.innerHTML = investigation.tags.map(tag => 
            `<span class="tag">${escapeHtml(tag)}</span>`
        ).join('');
    } else {
        tagsContainer.innerHTML = '<span style="color: var(--text-tertiary);">No tags</span>';
    }
    
    // ✅ FIX: Results display logic
    const results = investigation.results || [];
    document.getElementById('detailsResultCount').textContent = `${results.length} result${results.length !== 1 ? 's' : ''}`;
    
    const resultsContainer = document.getElementById('detailsResults');
    const emptyResults = document.getElementById('detailsEmptyResults');
    
    // ✅ FIX: Properly check if results exist
    if (!results || results.length === 0) {
        resultsContainer.innerHTML = '';
        resultsContainer.style.display = 'none';
        emptyResults.classList.remove('hidden');
    } else {
        resultsContainer.style.display = 'flex';
        emptyResults.classList.add('hidden');
        
        resultsContainer.innerHTML = results.map(result => `
            <div class="result-item">
                <div class="result-header">
                    <span class="result-tool">${escapeHtml(result.tool_name)}</span>
                    <span class="result-time">${formatDateTime(result.created_at)}</span>
                </div>
                <div class="result-target">Target: ${escapeHtml(result.target)}</div>
                <div class="result-threat">
                    <span class="threat-badge threat-${result.threat_level}">
                        ${getThreatIcon(result.threat_level)} ${result.threat_level.toUpperCase()}
                    </span>
                </div>
            </div>
        `).join('');
    }
    
    // Show modal
    document.getElementById('investigationDetailsModal').classList.remove('hidden');

    // Initialize AI chat
    initializeDashboardChat(investigation.id);

    if (hasAnalysisSummary(investigation)) {
        displayAnalysisResults(investigation.aiSummary, {
            analyzedAt: investigation.aiAnalyzedAt,
            scrollIntoView: false
        });
    }
}

function closeDetailsModal() {
    document.getElementById('investigationDetailsModal').classList.add('hidden');
    resetAnalysisSection();
    currentInvestigation = null;
}

// ==========================================================================
// UPDATE INVESTIGATION STATUS
// ==========================================================================

async function updateInvestigationStatus() {
    if (!currentInvestigation) return;
    
    const newStatus = document.getElementById('detailsStatus').value;
    
    try {
        const response = await fetch(`/api/investigations/${currentInvestigation.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        
        if (response.ok) {
            currentInvestigation.status = newStatus;
            showSuccess('Status updated successfully!');
            loadInvestigations(); // Reload to update the grid
        } else {
            showError('Failed to update status');
        }
    } catch (error) {
        console.error('Error updating status:', error);
        showError('Failed to update status');
    }
}

// ==========================================================================
// DELETE INVESTIGATION
// ==========================================================================

async function deleteInvestigation() {
    if (!currentInvestigation) return;
    
    if (!confirm(`Are you sure you want to delete "${currentInvestigation.name}"? This will also delete all associated results.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/investigations/${currentInvestigation.id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            closeDetailsModal();
            showSuccess('Investigation deleted successfully!');
            loadInvestigations();
        } else {
            showError('Failed to delete investigation');
        }
    } catch (error) {
        console.error('Error deleting investigation:', error);
        showError('Failed to delete investigation');
    }
}

// ==========================================================================
// EXPORT INVESTIGATION
// ==========================================================================

async function exportInvestigation() {
    if (!currentInvestigation) {
        showError('Select an investigation first.');
        return;
    }

    const results = currentInvestigation.results || [];
    if (results.length === 0) {
        showError('No results available to export.');
        return;
    }

    if (!hasAnalysisSummary(currentInvestigation)) {
        showError('Click "Analyze Investigation" first so the PDF can include AI analysis.');
        return;
    }

    try {
        const response = await fetch('/export-results', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                format: 'pdf',
                investigation: currentInvestigation,
                results,
                analysis_summary: currentInvestigation.aiSummary
            })
        });

        if (!response.ok) {
            let message = 'Failed to export PDF';

            try {
                const errorData = await response.json();
                if (errorData.error) {
                    message = errorData.error;
                }
            } catch (parseError) {
                console.error('Failed to parse export error response:', parseError);
            }

            throw new Error(message);
        }

        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        const safeName = (currentInvestigation.name || 'investigation-report')
            .replace(/[^a-z0-9-_]+/gi, '_')
            .replace(/^_+|_+$/g, '');

        link.href = downloadUrl;
        link.download = `${safeName || 'investigation-report'}.pdf`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(downloadUrl);

        showSuccess('PDF exported successfully!');
    } catch (error) {
        console.error('Error exporting investigation:', error);
        showError(error.message || 'Failed to export PDF');
    }
}

// ==========================================================================
// UTILITY FUNCTIONS
// ==========================================================================

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getThreatIcon(level) {
    const icons = {
        'critical': '🚨',
        'high': '⚠️',
        'medium': '⚡',
        'low': '📊',
        'safe': '✅'
    };
    return icons[level] || '📊';
}

function showSuccess(message) {
    // Simple alert for now - you can replace with a toast notification
    alert('✅ ' + message);
}

function showError(message) {
    // Simple alert for now - you can replace with a toast notification
    alert('❌ ' + message);
}

// ==========================================================================
// AI CHAT FUNCTIONALITY
// ==========================================================================

// AI Chat State
let dashboardChatMessages = [];

/**
 * Initialize AI chat when investigation modal opens
 */
function initializeDashboardChat(investigationId) {
    if (!investigationId) return;
    
    // Clear previous chat
    dashboardChatMessages = [];
    const messagesContainer = document.getElementById('dashboardChatMessages');
    if (messagesContainer) {
        messagesContainer.innerHTML = `
            <div class="empty-chat-state">
                <div class="empty-chat-icon">💬</div>
                <p>Ask me anything about this investigation!</p>
            </div>
        `;
    }
    
    // Add Enter key support
    const input = document.getElementById('dashboardChatInput');
    if (input) {
        const newInput = input.cloneNode(true);
        input.parentNode.replaceChild(newInput, input);
        
        newInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendDashboardMessage();
            }
        });
    }
    
    console.log('AI chat initialized for investigation:', investigationId);
}

/**
 * Send message from dashboard chat
 */
async function sendDashboardMessage() {
    const input = document.getElementById('dashboardChatInput');
    const sendBtn = document.getElementById('dashboardChatSendBtn');
    if (!input || !sendBtn) return;
    const message = input.value.trim();
    
    if (!message) return;
    
    if (!currentInvestigation) {
        alert('No investigation selected');
        return;
    }
    
    input.disabled = true;
    sendBtn.disabled = true;
    
    addDashboardMessage(message, 'user');
    input.value = '';
    
    showDashboardTyping(true);
    
    try {
        const response = await fetch('/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                investigation_id: currentInvestigation.id,
                message: message
            })
        });
        
        const data = await response.json();
        
        showDashboardTyping(false);
        
        if (data.success) {
            addDashboardMessage(data.response, 'bot', data.timestamp);
        } else {
            addDashboardMessage(`❌ ${data.error || 'Error occurred'}`, 'bot');
        }
        
    } catch (error) {
        console.error('Dashboard chat error:', error);
        showDashboardTyping(false);
        addDashboardMessage('Sorry, I encountered an error. Please try again.', 'bot');
    } finally {
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

/**
 * Ask a suggested question
 */
function askDashboardQuestion(question) {
    const input = document.getElementById('dashboardChatInput');
    if (input) {
        input.value = question;
        sendDashboardMessage();
    }
}

/**
 * Add message to chat UI
 */
function addDashboardMessage(text, sender, timestamp = null) {
    const messagesContainer = document.getElementById('dashboardChatMessages');
    const typingIndicator = document.getElementById('dashboardTypingIndicator');
    
    if (!messagesContainer) return;
    
    const emptyState = messagesContainer.querySelector('.empty-chat-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = `message-bubble ${sender}`;
    bubbleDiv.textContent = text;
    
    messageDiv.appendChild(bubbleDiv);
    
    if (timestamp) {
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = formatChatTimestamp(timestamp);
        messageDiv.appendChild(timeDiv);
    }
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    dashboardChatMessages.push({ text, sender, timestamp });
}

/**
 * Show/hide typing indicator
 */
function showDashboardTyping(show) {
    const indicator = document.getElementById('dashboardTypingIndicator');
    if (!indicator) return;
    
    if (show) {
        indicator.classList.add('active');
    } else {
        indicator.classList.remove('active');
    }
    
    const messagesContainer = document.getElementById('dashboardChatMessages');
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

/**
 * Format timestamp
 */
function formatChatTimestamp(timestamp) {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes} min${minutes > 1 ? 's' : ''} ago`;
    }
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    }
    return date.toLocaleString();
}

// ==========================================================================
// AI INVESTIGATION ANALYSIS
// ==========================================================================

function getAnalysisElements() {
    return {
        section: document.getElementById('aiAnalysisSection'),
        threatBadge: document.getElementById('overallThreatBadge'),
        threatIcon: document.getElementById('threatIcon'),
        threatText: document.getElementById('threatText'),
        summary: document.getElementById('executiveSummary'),
        insights: document.getElementById('keyInsights'),
        correlations: document.getElementById('correlationsContent'),
        actions: document.getElementById('recommendedActions'),
        button: document.getElementById('analyzeInvestigationBtn'),
        buttonText: document.getElementById('analyzeBtnText')
    };
}

function createSkeletonMarkup() {
    return '<div class="skeleton-loader"></div>';
}

function resetAnalysisSection() {
    const elements = getAnalysisElements();
    if (!elements.section) return;

    elements.section.classList.add('hidden');
    elements.threatBadge.className = 'threat-badge-large';
    elements.threatIcon.textContent = '🛡️';
    elements.threatText.textContent = 'ANALYZING...';

    [elements.summary, elements.insights, elements.correlations, elements.actions].forEach((container) => {
        if (container) {
            container.innerHTML = createSkeletonMarkup();
        }
    });

    if (elements.button) {
        elements.button.disabled = false;
    }

    if (elements.buttonText) {
        elements.buttonText.textContent = 'Analyze Investigation';
    }
}

async function analyzeInvestigation() {
    if (!currentInvestigation) {
        alert('No investigation selected');
        return;
    }

    const results = currentInvestigation.results || [];
    if (results.length === 0) {
        alert('No results to analyze. Run some OSINT tools first.');
        return;
    }

    const elements = getAnalysisElements();
    elements.section.classList.remove('hidden');

    const originalText = elements.buttonText.textContent;
    elements.button.disabled = true;
    elements.buttonText.textContent = `Analyzing ${results.length} results...`;

    showAnalysisLoading(true);

    try {
        const response = await fetch(`/ai/analyze/${currentInvestigation.id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (response.ok && data.success) {
            displayAnalysisResults(data.summary || {}, {
                analyzedAt: data.analyzed_at
            });
        } else {
            showAnalysisError(data.error || 'Analysis failed');
        }
    } catch (error) {
        console.error('Analysis error:', error);
        showAnalysisError('Failed to analyze investigation. Please try again.');
    } finally {
        elements.button.disabled = false;
        elements.buttonText.textContent = originalText;
    }
}

function displayAnalysisResults(summary, options = {}) {
    showAnalysisLoading(false);

    if (currentInvestigation) {
        currentInvestigation.aiSummary = summary;
        currentInvestigation.aiAnalyzedAt = options.analyzedAt || new Date().toISOString();
    }

    const elements = getAnalysisElements();
    const threatLevel = summary.overall_threat || 'medium';
    const threatIcons = {
        critical: '🔴',
        high: '🟠',
        medium: '🟡',
        low: '🟢',
        safe: '✅'
    };

    elements.threatBadge.className = `threat-badge-large threat-${threatLevel}`;
    elements.threatText.textContent = threatLevel.toUpperCase();
    elements.threatIcon.textContent = threatIcons[threatLevel] || '🛡️';

    elements.summary.innerHTML = formatAnalysisText(summary.summary);
    elements.insights.innerHTML = formatAnalysisText(summary.insights);
    elements.correlations.innerHTML = formatAnalysisText(summary.correlations);
    elements.actions.innerHTML = formatAnalysisText(summary.actions);

    elements.section.classList.remove('hidden');

    if (options.scrollIntoView !== false) {
        elements.section.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
        });
    }
}

function formatAnalysisText(text) {
    if (!text) return '<p class="no-data">No information available</p>';

    const lines = text
        .split('\n')
        .map((line) => line.trim())
        .filter(Boolean);

    if (lines.length === 0) {
        return '<p class="no-data">No information available</p>';
    }

    const htmlParts = [];
    let listItems = [];

    function flushList() {
        if (listItems.length > 0) {
            htmlParts.push(`<ul>${listItems.join('')}</ul>`);
            listItems = [];
        }
    }

    lines.forEach((line) => {
        if (/^[-•*]\s/.test(line)) {
            listItems.push(`<li>${escapeHtml(line.substring(2).trim())}</li>`);
            return;
        }

        if (/^\d+\.\s/.test(line)) {
            listItems.push(`<li>${escapeHtml(line.substring(line.indexOf('.') + 1).trim())}</li>`);
            return;
        }

        flushList();
        htmlParts.push(`<p>${escapeHtml(line)}</p>`);
    });

    flushList();

    return htmlParts.join('');
}

function showAnalysisLoading(show) {
    const elements = getAnalysisElements();
    if (!elements.section) return;

    [elements.summary, elements.insights, elements.correlations, elements.actions].forEach((container) => {
        if (container) {
            container.innerHTML = show ? createSkeletonMarkup() : container.innerHTML;
        }
    });

    if (show) {
        elements.threatBadge.className = 'threat-badge-large';
        elements.threatText.textContent = 'ANALYZING...';
        elements.threatIcon.textContent = '⏳';
    }
}

function showAnalysisError(errorMessage) {
    showAnalysisLoading(false);

    const elements = getAnalysisElements();
    const errorHtml = `<p class="error-message">❌ ${escapeHtml(errorMessage)}</p>`;

    elements.summary.innerHTML = errorHtml;
    elements.insights.innerHTML = '<p class="no-data">No insights available</p>';
    elements.correlations.innerHTML = '<p class="no-data">No correlations available</p>';
    elements.actions.innerHTML = '<p class="no-data">No actions available</p>';

    elements.threatBadge.className = 'threat-badge-large';
    elements.threatText.textContent = 'ERROR';
    elements.threatIcon.textContent = '⚠️';
}

function closeAnalysis() {
    const elements = getAnalysisElements();
    if (!elements.section) return;
    elements.section.classList.add('hidden');
}

function hasAnalysisSummary(investigation) {
    return Boolean(
        investigation &&
        investigation.aiSummary &&
        (
            investigation.aiSummary.summary ||
            investigation.aiSummary.insights ||
            investigation.aiSummary.correlations ||
            investigation.aiSummary.actions
        )
    );
}
