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
