class UIModule {
    constructor() {
        this.theme = localStorage.getItem("theme") || "dark";
        this.applyTheme(this.theme);
    }

    // 🎨 SAFE theme switching
    applyTheme(theme) {
        const validThemes = ["dark", "light", "cyber"];

        if (!validThemes.includes(theme)) {
            theme = "dark";
        }

        document.body.classList.remove(
            "dark-theme",
            "light-theme",
            "cyber-theme"
        );

        document.body.classList.add(`${theme}-theme`);

        this.theme = theme;
        localStorage.setItem("theme", theme);
    }

    toggleTheme() {
        const themes = ["dark", "light", "cyber"];
        const current = themes.indexOf(this.theme);

        const nextTheme = themes[(current + 1) % themes.length];
        this.applyTheme(nextTheme);
    }

    // 🆔 session UI
    updateSessionInfo() {
        const el = document.getElementById("sessionId");
        const session = window.jarvis?.sessionId;

        if (el && session) {
            el.textContent = session.slice(0, 8);
        }
    }

    // 📊 message counter helper (NEW)
    updateMessageCount(count) {
        const el = document.getElementById("msgCount");
        if (el) el.textContent = count;
    }

    // ⚡ response time helper (NEW)
    updateResponseTime(ms) {
        const el = document.getElementById("responseTime");
        if (el) el.textContent = `${ms}ms`;
    }

    // 🔔 toast system (VERY USEFUL)
    showToast(message, type = "info") {
        const toast = document.getElementById("toastNotification");
        const text = document.getElementById("toastMessage");

        if (!toast || !text) return;

        text.textContent = message;

        toast.className = `toast-notification ${type} active`;

        setTimeout(() => {
            toast.classList.remove("active");
        }, 3000);
    }
}
