class Utils {
    static formatTime() {
        return new Date().toLocaleTimeString();
    }

    // ✅ FIXED: modern safe ID generator
    static generateId() {
        return `${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
    }
}
