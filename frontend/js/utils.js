class Utils {

    // 🕒 Current time (safe + readable format)
    static formatTime() {
        return new Date().toLocaleTimeString();
    }

    // 📅 Date (useful for chat logs / UI)
    static formatDate() {
        return new Date().toLocaleDateString();
    }

    // 🆔 Unique ID (safe for messages, sessions, uploads)
    static generateId() {
        return `${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    }

    // ✂️ Safe text trim (prevents undefined crashes)
    static safeText(text, fallback = "") {
        return (text ?? "").toString().trim() || fallback;
    }

    // 🔢 Clamp numbers (useful for sliders like voice rate/pitch)
    static clamp(num, min, max) {
        num = Number(num);
        if (isNaN(num)) return min;
        return Math.max(min, Math.min(max, num));
    }

    // 📦 LocalStorage safe read
    static getStorage(key, fallback = null) {
        try {
            const val = localStorage.getItem(key);
            return val === null ? fallback : val;
        } catch {
            return fallback;
        }
    }

    // 💾 LocalStorage safe write
    static setStorage(key, value) {
        try {
            localStorage.setItem(key, value);
        } catch (e) {
            console.warn("Storage error:", e);
        }
    }

    // ⚡ Debounce (VERY useful for input, search, voice UI)
    static debounce(func, delay = 300) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => func(...args), delay);
        };
    }

    // 🎯 Check empty values safely
    static isEmpty(value) {
        return value === null || value === undefined || value.toString().trim() === "";
    }
}
