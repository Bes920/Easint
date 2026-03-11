/**
 * Theme Manager for EASINT Platform
 * Handles theme switching with system preference detection and localStorage persistence
 */

class ThemeManager {
    constructor() {
        this.themes = ['system', 'dark', 'light', 'neon'];
        this.storageKey = 'easint-theme';
        this.init();
    }

    init() {
        // Apply saved theme or system preference
        this.loadTheme();
        
        // Setup theme toggle button
        this.setupThemeToggle();
        
        // Listen for system theme changes
        this.listenToSystemTheme();
    }

    loadTheme() {
        const savedTheme = localStorage.getItem(this.storageKey) || 'system';
        this.setTheme(savedTheme);
    }

    setTheme(theme) {
        if (!this.themes.includes(theme)) theme = 'system';
        
        let actualTheme = theme;
        
        // If system theme, detect preference
        if (theme === 'system') {
            actualTheme = this.getSystemTheme();
        }
        
        // Apply theme to HTML element
        document.documentElement.setAttribute('data-theme', actualTheme);
        localStorage.setItem(this.storageKey, theme);
        
        // Update theme button appearance
        this.updateThemeButton(theme);
    }

    getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
            return 'light';
        }
        return 'dark';
    }

    setupThemeToggle() {
        const themeBtn = document.getElementById('themeToggle');
        const themeMenu = document.getElementById('themeMenu');
        const themeOptions = document.querySelectorAll('.theme-option');

        if (!themeBtn) return;

        // Toggle menu visibility
        themeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            themeMenu.classList.toggle('active');
        });

        // Close menu when clicking outside
        document.addEventListener('click', () => {
            themeMenu.classList.remove('active');
        });

        // Handle theme option selection
        themeOptions.forEach(option => {
            option.addEventListener('click', () => {
                const theme = option.getAttribute('data-theme');
                this.setTheme(theme);
                themeMenu.classList.remove('active');
            });
        });
    }

    updateThemeButton(currentTheme) {
        const themeOptions = document.querySelectorAll('.theme-option');
        
        themeOptions.forEach(option => {
            if (option.getAttribute('data-theme') === currentTheme) {
                option.classList.add('active');
            } else {
                option.classList.remove('active');
            }
        });

        // Update icon
        const themeIcon = document.querySelector('.theme-icon');
        const iconMap = {
            'system': '🖥️',
            'dark': '🌙',
            'light': '☀️',
            'neon': '⚡'
        };
        if (themeIcon) {
            themeIcon.textContent = iconMap[currentTheme] || '🌙';
        }
    }

    listenToSystemTheme() {
        if (window.matchMedia) {
            const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
            darkModeQuery.addEventListener('change', () => {
                const savedTheme = localStorage.getItem(this.storageKey) || 'system';
                if (savedTheme === 'system') {
                    const newTheme = this.getSystemTheme();
                    document.documentElement.setAttribute('data-theme', newTheme);
                }
            });
        }
    }
}

// Initialize theme manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new ThemeManager();
    });
} else {
    new ThemeManager();
}
async function loadInvestigationsDropdown() {
    try {
        const response = await fetch('/api/investigations');
        const data = await response.json();

        const dropdown = document.getElementById('currentInvestigation');

        if (data.success && data.investigations.length > 0) {
            // Clear loading option
            dropdown.innerHTML = '';

            // Add "Auto-saved Results" as default
            const autoOption = document.createElement('option');
            autoOption.value = 'auto';
            autoOption.textContent = '📁 Auto-saved Results (Default)';
            dropdown.appendChild(autoOption);

            // Add all other investigations
            data.investigations.forEach(inv => {
                // Skip "Auto-saved Results" since we already added it
                if (inv.name === 'Auto-saved Results') return;

                const option = document.createElement('option');
                option.value = inv.id;
                option.textContent = `📊 ${inv.name}`;
                dropdown.appendChild(option);
            });

            // Try to restore last selected investigation
            const lastSelected = localStorage.getItem('selectedInvestigation');
            if (lastSelected) {
                dropdown.value = lastSelected;
            }

            // Save selection when changed
            dropdown.addEventListener('change', function() {
                localStorage.setItem('selectedInvestigation', this.value);
                console.log(`✅ Results will now save to: ${this.options[this.selectedIndex].text}`);
            });

        } else {
            dropdown.innerHTML = '<option value="auto">📁 Auto-saved Results (Default)</option>';
        }

    } catch (error) {
        console.error('Failed to load investigations:', error);
        const dropdown = document.getElementById('currentInvestigation');
        dropdown.innerHTML = '<option value="auto">📁 Auto-saved Results (Default)</option>';
    }
}

// Get currently selected investigation ID
function getCurrentInvestigationId() {
    const dropdown = document.getElementById('currentInvestigation');
    const value = dropdown.value;

    // If 'auto' or empty, return null (will use default "Auto-saved Results")
    if (value === 'auto' || value === '') {
        return null;
    }

    return value;
}

// Load dropdown when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadInvestigationsDropdown();
});
