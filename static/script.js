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
        
        this.themeToggle.addEventListener('click', () => this.toggleTheme());
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
        this.body.setAttribute('data-theme', theme);
        this.saveTheme(theme);
        this.updateToggleState(theme);
    }

    toggleTheme() {
        const newTheme = this.body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
    }
    
    updateToggleState(theme) {
        if (!this.themeToggle) return;
        if (theme === 'dark') {
            this.themeToggle.classList.remove('light');
            this.themeToggle.classList.add('dark');
        } else {
            this.themeToggle.classList.remove('dark');
            this.themeToggle.classList.add('light');
        }
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