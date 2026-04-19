// Utility functions
class Utils {
    static formatDate(date) {
        return new Date(date).toLocaleString();
    }
    
    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    static generateId() {
        return Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Make globally available
window.Utils = Utils;
