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
// EXPORT INVESTIGATION (Placeholder)
// ==========================================================================

function exportInvestigation() {
    if (!currentInvestigation) return;
    showError('PDF export feature coming soon!');
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
