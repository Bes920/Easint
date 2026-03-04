// OPSEC Academy JavaScript - Simplified

document.addEventListener('DOMContentLoaded', function() {
    
    // Module toggle functionality
    window.toggleModule = function(header) {
        const module = header.parentElement;
        module.classList.toggle('open');
    };
    
    // Scroll to module
    window.scrollToModule = function(moduleId) {
        const module = document.getElementById(moduleId);
        if (module) {
            module.scrollIntoView({ behavior: 'smooth', block: 'start' });
            // Update active state in TOC
            document.querySelectorAll('.toc-item').forEach(item => {
                item.classList.remove('active');
            });
            const tocLink = document.querySelector(`[onclick="scrollToModule('${moduleId}')"]`);
            if (tocLink) {
                tocLink.classList.add('active');
            }
        }
    };
    
    // Progress tracking
    window.updateProgress = function() {
        const allCheckboxes = document.querySelectorAll('.checkbox-item input[type="checkbox"]');
        const checkedBoxes = document.querySelectorAll('.checkbox-item input[type="checkbox"]:checked');
        
        const total = allCheckboxes.length;
        const checked = checkedBoxes.length;
        const percentage = total > 0 ? Math.round((checked / total) * 100) : 0;
        
        const progressBar = document.getElementById('progressBar');
        const progressPercent = document.getElementById('progressPercent');
        
        if (progressBar) {
            progressBar.style.width = percentage + '%';
        }
        if (progressPercent) {
            progressPercent.textContent = percentage + '%';
        }
    };
    
    // Initialize progress on load
    updateProgress();
    
    // Smooth scroll for internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // Update active TOC item on scroll
    const modules = document.querySelectorAll('.opsec-module');
    const tocLinks = document.querySelectorAll('.toc-item');
    
    function updateActiveTOC() {
        let currentModule = '';
        
        modules.forEach(module => {
            const rect = module.getBoundingClientRect();
            if (rect.top <= 150 && rect.bottom >= 150) {
                currentModule = module.id;
            }
        });
        
        if (currentModule) {
            tocLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('onclick') && link.getAttribute('onclick').includes(currentModule)) {
                    link.classList.add('active');
                }
            });
        }
    }
    
    window.addEventListener('scroll', updateActiveTOC);
    updateActiveTOC(); // Initial call
});
