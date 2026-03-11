/**
 * EASINT - Investigation Dashboard
 * Complete investigation management system
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
    
    // Search and filters
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
        renderInvestigations(investigations);
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
    
    loading.classList.add('hidden');
    
    if (investigationsToRender.length === 0) {
        grid.innerHTML = '';
        empty.classList.remove('hidden');
        return;
    }
    
    empty.classList.add('hidden');
    
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
// FILTER INVESTIGATIONS
// ==========================================================================

function filterInvestigations() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;
    const sortFilter = document.getElementById('sortFilter').value;
    
    let filtered = [...investigations];
    
    // Filter by search
    if (searchTerm) {
        filtered = filtered.filter(inv => 
            inv.name.toLowerCase().includes(searchTerm) ||
            (inv.description && inv.description.toLowerCase().includes(searchTerm)) ||
            (inv.tags && inv.tags.some(tag => tag.toLowerCase().includes(searchTerm)))
        );
    }
    
    // Filter by status
    if (statusFilter !== 'all') {
        filtered = filtered.filter(inv => inv.status === statusFilter);
    }
    
    // Sort
    filtered.sort((a, b) => {
        switch (sortFilter) {
            case 'newest':
                return new Date(b.created_at) - new Date(a.created_at);
            case 'oldest':
                return new Date(a.created_at) - new Date(b.created_at);
            case 'most-results':
                return (b.result_count || 0) - (a.result_count || 0);
            case 'highest-threat':
                return getThreatValue(b.threat_level) - getThreatValue(a.threat_level);
            default:
                return 0;
        }
    });
    
    renderInvestigations(filtered);
}

function getThreatValue(level) {
    const values = { 'critical': 5, 'high': 4, 'medium': 3, 'low': 2, 'safe': 1 };
    return values[level] || 0;
}

// ==========================================================================
// CREATE INVESTIGATION MODAL
// ==========================================================================

function openCreateModal() {
    document.getElementById('createInvestigationModal').classList.remove('hidden');
    document.getElementById('investigationName').focus();
}

function closeCreateModal() {
    document.getElementById('createInvestigationModal').classList.add('hidden');
    document.getElementById('createInvestigationForm').reset();
}

async function createInvestigation(e) {
    e.preventDefault();
    
    const name = document.getElementById('investigationName').value.trim();
    const description = document.getElementById('investigationDescription').value.trim();
    const tagsInput = document.getElementById('investigationTags').value.trim();
    const tags = tagsInput ? tagsInput.split(',').map(t => t.trim()).filter(t => t) : [];
    
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
            currentInvestigation = data;
            showInvestigationDetails(data);
        } else {
            showError('Failed to load investigation details');
        }
    } catch (error) {
        console.error('Error loading investigation:', error);
        showError('Failed to load investigation details');
    }
}

function showInvestigationDetails(investigation) {
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
    
    // Set results
    const results = investigation.results || [];
    document.getElementById('detailsResultCount').textContent = `${results.length} result${results.length !== 1 ? 's' : ''}`;
    
    const resultsContainer = document.getElementById('detailsResults');
    const emptyResults = document.getElementById('detailsEmptyResults');
    
    if (results.length === 0) {
        resultsContainer.classList.add('hidden');
        emptyResults.classList.remove('hidden');
    } else {
        resultsContainer.classList.remove('hidden');
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
}

function closeDetailsModal() {
    document.getElementById('investigationDetailsModal').classList.add('hidden');
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
            showSuccess('Status updated successfully!');
            loadInvestigations(); // Reload to update cards
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
            loadInvestigations(); // Reload to update list
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

function exportInvestigation() {
    if (!currentInvestigation) return;
    
    showInfo('PDF export coming soon! For now, you can copy the data from this view.');
}

// ==========================================================================
// UTILITY FUNCTIONS
// ==========================================================================

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getThreatIcon(level) {
    const icons = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🔵',
        'safe': '🟢'
    };
    return icons[level] || '⚪';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==========================================================================
// NOTIFICATIONS
// ==========================================================================

function showSuccess(message) {
    showNotification(message, 'success');
}

function showError(message) {
    showNotification(message, 'error');
}

function showInfo(message) {
    showNotification(message, 'info');
}

function showNotification(message, type) {
    // Simple alert for now - can be enhanced with custom notification UI
    alert(message);
}
