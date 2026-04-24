class Utils {
    static formatTime() {
        return new Date().toLocaleTimeString();
    }

    static generateId() {
        return Date.now() + "_" + Math.random().toString(36).substr(2, 5);
    }
}