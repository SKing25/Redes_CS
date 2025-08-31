// ================================
// MÓDULO: ThemeManager 
// ================================
class ThemeManager {
    constructor() {
        this.themeToggle = document.getElementById('themeToggle');
        this.body = document.body;
        this.init();
    }
    
    init() {
        if (!this.themeToggle) return;
        
        const savedTheme = this.getSavedTheme() || 'light';
        this.applyTheme(savedTheme);
        
        this.themeToggle.addEventListener('change', () => this.toggleTheme());
    }
    
    getSavedTheme() {
        try {
            return localStorage.getItem('theme') || this.getCookieTheme() || window.currentTheme || 'light';
        } catch (e) {
            return this.getCookieTheme() || window.currentTheme || 'light';
        }
    }
    
    saveTheme(theme) {
        try {
            localStorage.setItem('theme', theme);
        } catch (e) {
            console.warn('localStorage no disponible, usando cookies');
            this.setCookieTheme(theme);
        }
        window.currentTheme = theme;
    }
    
    applyTheme(theme) {
        // Aplicar clase al body (para que coincida con el CSS)
        if (theme === 'dark') {
            this.body.classList.add('dark-mode');
            this.themeToggle.checked = true;
        } else {
            this.body.classList.remove('dark-mode');
            this.themeToggle.checked = false;
        }
        
        this.saveTheme(theme);
    }

    toggleTheme() {
        const isDark = this.themeToggle.checked;
        const newTheme = isDark ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }
    
    setCookieTheme(theme) {
        document.cookie = `theme=${theme};path=/;max-age=${60 * 60 * 24 * 365}`;
    }
    
    getCookieTheme() {
        const name = 'theme=';
        const decodedCookie = decodeURIComponent(document.cookie);
        const ca = decodedCookie.split(';');
        for(let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') {
                c = c.substring(1);
            }
            if (c.indexOf(name) === 0) {
                return c.substring(name.length, c.length);
            }
        }
        return '';
    }
}

// ================================
// MÓDULO: PageSelector
// ================================
class PageSelector {
    constructor() {
        this.pageItems = document.querySelectorAll('.page-item');
        this.init();
    }

    init() {
        const currentPage = window.location.pathname.split('/').pop();
        this.pageItems.forEach(item => {
            const dataPage = item.getAttribute('data-page') + '.html';
            if (dataPage === currentPage) {
                item.classList.add('active');
            }
        });
    }
}

// ================================
// INICIALIZACIÓN
// ================================
window.addEventListener('load', () => {
    new ThemeManager();
    new PageSelector();
});